"""Alertas contextuais de upgrade no dashboard — máquina de assinaturas."""

from __future__ import annotations

from flask import url_for

from db import (
    count_band_cifras,
    count_band_members,
    count_band_setlists,
    get_owned_bands,
)
from monetizacao import (
    LIMITES_COLECAO_GRATIS,
    LIMITES_GRATIS,
    PLANO_GRATIS,
    PLANO_INDIVIDUAL,
    PLANO_PRO,
    PLANOS,
    PRECO_ESTUDIO_PREMIUM,
    dias_restantes_trial,
    dias_restantes_trial_estudio,
    get_plano_efetivo,
    studio_tem_premium,
    user_pode_compartilhar_cifras,
    user_tem_assinatura_ativa,
)

_PRECO_PRO = int(PLANOS[PLANO_PRO].preco_mensal or 29)
_PRECO_INDIVIDUAL = int(PLANOS[PLANO_INDIVIDUAL].preco_mensal or 15)
_PRECO_ESTUDIO = int(PRECO_ESTUDIO_PREMIUM)


def _planos_checkout(plano: str, banda_id: str | None = None) -> str:
    kwargs = {"plano": plano, "go": 1}
    if banda_id:
        kwargs["banda_id"] = banda_id
    return url_for("assinatura_bp.planos", **kwargs)


def _near_limit_message(current: int, limit: int, recurso: str) -> str | None:
    if limit <= 0:
        return (
            f"No Grátis não há {recurso} de ensaio. "
            f"Pro (R$ {_PRECO_PRO}/mês) libera setlist, Modo Tocar, PDF e offline."
        )
    if current < max(1, limit - 1):
        return None
    if current >= limit:
        return (
            f"Limite do Grátis: {current}/{limit} {recurso}. "
            f"No Pro (R$ {_PRECO_PRO}/mês) isso fica ilimitado + PDF + offline."
        )
    return (
        f"Você usa {current} de {limit} {recurso}. "
        f"Pro libera tudo por R$ {_PRECO_PRO}/mês — cancele quando quiser."
    )


def get_dashboard_upsells(
    user_id: str, *, owned_bands: list | None = None
) -> list[dict]:
    """Banners de conversão baseados em uso real — prioriza pagar."""
    bands = owned_bands if owned_bands is not None else get_owned_bands(user_id)
    alerts: list[dict] = []

    if not bands and not user_tem_assinatura_ativa(user_id):
        from db import user_play_mode_used
        from demo_onboarding import count_real_personal_cifras

        n_cifras = count_real_personal_cifras(user_id)
        played = user_play_mode_used(user_id)
        if played and n_cifras >= max(3, LIMITES_COLECAO_GRATIS - 2):
            alerts.insert(
                0,
                {
                    "level": "warning",
                    "title": f"Coleção quase cheia · Individual R$ {_PRECO_INDIVIDUAL}",
                    "message": (
                        f"Você tem {n_cifras}/{LIMITES_COLECAO_GRATIS} cifras no Grátis. "
                        "Individual libera repertório e Modo Tocar ilimitados, PDF e offline."
                    ),
                    "cta_label": f"Assinar Individual — R$ {_PRECO_INDIVIDUAL}",
                    "cta_url": _planos_checkout(PLANO_INDIVIDUAL),
                },
            )
        elif n_cifras >= 1:
            alerts.append(
                {
                    "level": "info",
                    "title": "Plano Individual — toca só",
                    "message": (
                        f"Você tem {n_cifras}/{LIMITES_COLECAO_GRATIS} cifras no Grátis. "
                        f"Individual (R$ {_PRECO_INDIVIDUAL}/mês) libera repertório ilimitado, PDF e offline."
                    ),
                    "cta_label": f"Assinar Individual — R$ {_PRECO_INDIVIDUAL}",
                    "cta_url": _planos_checkout(PLANO_INDIVIDUAL),
                }
            )
        if not bands:
            alerts.append(
                {
                    "level": "success",
                    "title": "Toca em banda ou ministério?",
                    "message": (
                        "Crie sua banda grátis para montar a 1ª setlist do ensaio "
                        "e chamar o grupo no WhatsApp."
                    ),
                    "cta_label": "Criar minha banda grátis",
                    "cta_url": url_for("bands.create", bem_vindo=1),
                }
            )

    for band in bands:
        band_id = band["id"]
        name = band.get("name") or "sua banda"
        plano = get_plano_efetivo(band_id)
        planos_url = _planos_checkout(PLANO_PRO, band_id)

        dias = dias_restantes_trial(band_id)
        if dias is not None:
            if dias <= 7:
                alerts.append(
                    {
                        "level": "warning" if dias <= 3 else "success",
                        "title": f"Trial Pro — {dias} dia(s) · {name}",
                        "message": (
                            "Assine agora para não perder PDF, offline e Modo Tocar da banda."
                        ),
                        "cta_label": f"Assinar Pro — R$ {_PRECO_PRO}",
                        "cta_url": planos_url,
                    }
                )
            continue

        if plano != PLANO_GRATIS:
            continue

        for label, limit, counter, recurso in (
            ("músicas", LIMITES_GRATIS["musica"], count_band_cifras, "músicas"),
            ("setlists", LIMITES_GRATIS["setlist"], count_band_setlists, "setlists"),
            (
                "integrantes",
                LIMITES_GRATIS["integrante"],
                count_band_members,
                "integrantes",
            ),
        ):
            msg = _near_limit_message(counter(band_id), limit, recurso)
            if msg:
                alerts.append(
                    {
                        "level": "info",
                        "title": f"Limite · {name}",
                        "message": msg,
                        "cta_label": f"Assinar Pro — R$ {_PRECO_PRO}",
                        "cta_url": planos_url,
                    }
                )
                break
        else:
            alerts.append(
                {
                    "level": "info",
                    "title": f"Quer PDF, offline e setlists ilimitadas em {name}?",
                    "message": (
                        f"O Pro libera exportação em PDF, pacote offline no palco, "
                        f"setlists e músicas ilimitadas por R$ {_PRECO_PRO}/mês."
                    ),
                    "cta_label": f"Conhecer o Pro — R$ {_PRECO_PRO}",
                    "cta_url": planos_url,
                }
            )

    # Estúdio
    try:
        from models_studio import get_or_create_studio_subscription, get_studio_by_owner

        studio = get_studio_by_owner(user_id)
        if studio:
            sub = get_or_create_studio_subscription(user_id)
            if not studio_tem_premium(user_id, sub):
                dias_e = dias_restantes_trial_estudio(user_id)
                if dias_e is not None and dias_e <= 7:
                    alerts.append(
                        {
                            "level": "warning",
                            "title": f"Trial Estúdio — {dias_e} dia(s)",
                            "message": f"Premium R$ {_PRECO_ESTUDIO}/mês · salas ilimitadas.",
                            "cta_label": f"Assinar Estúdio — R$ {_PRECO_ESTUDIO}",
                            "cta_url": url_for("assinatura_bp.planos") + "#estudio",
                        }
                    )
                else:
                    try:
                        from models_studio import list_rooms

                        n_rooms = (
                            len(list_rooms(studio["id"])) if studio.get("id") else 0
                        )
                    except Exception:
                        n_rooms = 0
                    if n_rooms >= 2:
                        alerts.append(
                            {
                                "level": "warning",
                                "title": "3ª sala = Estúdio Premium",
                                "message": (
                                    f"No Básico cabem 2 salas. Premium R$ {_PRECO_ESTUDIO}/mês "
                                    "libera salas ilimitadas."
                                ),
                                "cta_label": f"Assinar Premium — R$ {_PRECO_ESTUDIO}",
                                "cta_url": url_for("assinatura_bp.planos") + "#estudio",
                            }
                        )
                    else:
                        alerts.append(
                            {
                                "level": "info",
                                "title": "Estúdio Premium",
                                "message": (
                                    f"Salas ilimitadas e destaque — R$ {_PRECO_ESTUDIO}/mês."
                                ),
                                "cta_label": f"Assinar Premium — R$ {_PRECO_ESTUDIO}",
                                "cta_url": url_for("assinatura_bp.planos") + "#estudio",
                            }
                        )
    except Exception:
        pass

    if bands and not user_pode_compartilhar_cifras(user_id):
        pass  # coberto pelos alertas de Pro acima

    # Dedup por título
    seen: set[str] = set()
    out: list[dict] = []
    for a in alerts:
        key = a.get("title") or ""
        if key in seen:
            continue
        seen.add(key)
        out.append(a)
    return out[:5]


def show_referral_card(user_id: str) -> bool:
    """Indicação após primeira setlist OU após usar Modo Tocar."""
    from db import user_play_mode_used

    if user_play_mode_used(user_id):
        return True
    for band in get_owned_bands(user_id):
        if count_band_setlists(band["id"]) > 0:
            return True
    return False


def referral_members_url(user_id: str) -> str | None:
    """Primeira banda própria para atalho de convite."""
    bands = get_owned_bands(user_id)
    if not bands:
        return None
    return url_for("bands.members", band_id=bands[0]["id"])
