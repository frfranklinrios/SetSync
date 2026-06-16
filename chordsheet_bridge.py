"""Ponte entre cifras SetSync e o módulo chordsheet (formato chordsheet.com)."""

from __future__ import annotations

import json
from typing import Any

from chordsheet.export import MODULE_ID, chart_to_payload, payload_to_chart
from chordsheet.parser import Chart, parse_chart
from chordsheet.private_notes import (
    apply_private_notes_to_payload,
    extract_and_store_private_notes,
    merge_private_notes,
    split_private_notes,
)
from chordsheet.render import render_chart_html
from chordsheet.transpose import transpose_chart
from leadsheet.converter import is_leadsheet_document, resolve_to_grade_flat


def _chordsheet_source_text(data: dict[str, Any]) -> str:
    """Retorna texto chordsheet.com; LeadSheet legado usa source como dict."""
    src = data.get("source")
    if isinstance(src, str):
        return src.strip()
    return ""


def _parse_stored_chordsheet(raw) -> dict[str, Any] | None:
    if not raw:
        return None
    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(data, dict):
        return None
    if is_leadsheet_document(data):
        return None
    source_text = _chordsheet_source_text(data)
    if data.get("module") == MODULE_ID and source_text:
        return data
    if source_text and data.get("meta") is not None:
        return data
    return None


def load_stored_chordsheet(cifra: dict) -> dict[str, Any] | None:
    for field in ("chordsheet_json", "leadsheet_json"):
        data = _parse_stored_chordsheet(cifra.get(field))
        if data:
            return data
    return None


def _bar_acordes_for_grade(bar) -> list[str]:
    """Achata pulse_grid para grade legado (inclui semi-pulsos C&D)."""
    if bar.is_empty or bar.simile or bar.chords in (["%"], [""]):
        return ["%"]
    out: list[str] = []
    for beat in bar.get_pulse_grid():
        for c in beat:
            token = str(c or "").strip()
            if token in ("", "%"):
                continue
            if token == "*":
                out.append("%")
            else:
                out.append(token)
    return out or ["%"]


def chart_to_grade_flat(chart: Chart) -> list[dict]:
    """Converte Chart para grade plana (compatível com play mode legado)."""
    sec_at = {i: t for i, t in chart.sections}
    result: list[dict] = []
    bar_num = 0
    for i, bar in enumerate(chart.bars):
        if bar.blank_spacer or bar.private_note:
            continue
        if bar.nav:
            continue
        if bar.annotation and not bar.chords and not bar.is_empty:
            continue
        bar_num += 1
        item: dict = {"compasso": bar_num, "acordes": _bar_acordes_for_grade(bar)}
        if i in sec_at:
            item["secao"] = sec_at[i]
        result.append(item)
    return result


def load_editor_initial(cifra: dict, user_id: str | None = None) -> dict[str, Any]:
    """Estado inicial do editor Chord Sheet para uma cifra."""
    saved_at = cifra.get("updated_at")
    stored = load_stored_chordsheet(cifra)
    if stored:
        view = apply_private_notes_to_payload(stored, user_id)
        out = {
            "source": view.get("source") or "",
            "meta": view.get("meta") or {},
            "prefs": view.get("prefs") or {},
        }
        if saved_at:
            out["saved_at"] = str(saved_at)
        return out

    flat = resolve_to_grade_flat(cifra)
    bpm = cifra.get("bpm")
    meta = {
        "title": (cifra.get("titulo") or "").strip() or "Sem título",
        "artist": (cifra.get("artista") or "").strip(),
        "key": (cifra.get("tom_original") or "").strip(),
        "bpm": str(int(bpm)) if bpm else "",
        "time_signature": "4/4",
        "capo": "",
        "style": "",
    }
    return {
        "source": grade_flat_to_source(flat) if flat else "",
        "meta": meta,
        "prefs": {},
        **({"saved_at": str(saved_at)} if saved_at else {}),
    }


def _beats_per_bar_for_grade(acordes: list, default: int = 4) -> int:
    n = len(acordes or [])
    if n in (2, 3, 4, 6, 8, 12):
        return n
    return default


def _grade_acordes_to_source_line(acordes: list, *, beats_per_bar: int | None = None) -> str:
    """
    Converte acordes de um compasso legado → token chordsheet.

    Espaço = compasso; underscore = pulso no mesmo compasso (ver docs/chordsheet-formato.md).
    Ex.: ['Cm','%','%','%'] → 'Cm' (figura 1: acorde no 1º pulso).
    Ex.: ['C','Am','F','G'] → 'C_Am_F_G' (um compasso, quatro pulsos).
    """
    if not acordes:
        return "*"
    bpb = beats_per_bar or _beats_per_bar_for_grade(acordes)
    slots = [str(a).strip() or "%" for a in acordes]
    while len(slots) < bpb:
        slots.append("%")
    slots = slots[:bpb]

    if all(s in ("%", "*", "") for s in slots):
        return "%"

    # Um acorde no primeiro pulso; demais % → só o acorde (render preenche com ·)
    if slots[0] not in ("%", "*", "") and all(
        s in ("%", "*", "") for s in slots[1:]
    ):
        return slots[0]

    parts: list[str] = []
    for s in slots:
        parts.append("*" if s in ("%", "*", "") else s)
    while len(parts) > 1 and parts[-1] == "*":
        parts.pop()
    if not parts or all(p == "*" for p in parts):
        return "*"
    if len(parts) == 1:
        return parts[0]
    return "_".join(parts)


def grade_flat_to_source(grade_list: list[dict]) -> str:
    """Converte grade plana (LeadSheet) em texto estilo chordsheet.com."""
    lines: list[str] = []
    last_secao: str | None = None
    for item in grade_list or []:
        if not isinstance(item, dict):
            continue
        secao = (item.get("secao") or "").strip()
        if secao and secao != last_secao:
            lines.append(f"= {secao}")
            last_secao = secao
        acordes = item.get("acordes") or ["%"]
        if not isinstance(acordes, list):
            acordes = ["%"]
        lines.append(_grade_acordes_to_source_line(acordes))
    return "\n".join(lines).strip()


def cifra_chart_payload(
    cifra: dict,
    *,
    grade_list: list[dict] | None = None,
) -> dict[str, Any] | None:
    """Monta {source, meta, prefs} para parse_chart (tom nativo, sem transposição de palco)."""
    stored = load_stored_chordsheet(cifra)
    if stored:
        return {
            "source": stored["source"],
            "meta": dict(stored.get("meta") or {}),
            "prefs": stored.get("prefs") or {},
        }

    flat = grade_list if grade_list is not None else resolve_to_grade_flat(cifra)
    if not flat:
        return None

    bpm = cifra.get("bpm")
    meta = {
        "title": (cifra.get("titulo") or "").strip() or "Sem título",
        "artist": (cifra.get("artista") or "").strip(),
        "key": (cifra.get("tom_original") or "").strip(),
        "bpm": str(int(bpm)) if bpm else "",
        "time_signature": "4/4",
    }
    return {"source": grade_flat_to_source(flat), "meta": meta, "prefs": {}}


def chordsheet_performance_semitones(
    cifra: dict,
    performance_semitones: int = 0,
    *,
    chart_source_key: str | None = None,
) -> tuple[int, str]:
    """Semitons para o chord sheet chegar ao mesmo tom da cifra transposta."""
    from util import (
        key_at_transpose,
        normalize_tom_label,
        normalize_transpose_semitones,
        semitones_between_keys,
    )

    performance = normalize_transpose_semitones(performance_semitones)
    tom_orig = normalize_tom_label(cifra.get("tom_original") or "")
    target_key = key_at_transpose(tom_orig, performance)
    source_key = normalize_tom_label(chart_source_key or tom_orig)
    chart_semi = semitones_between_keys(source_key, target_key)
    return chart_semi, target_key


def cifra_has_chordsheet(cifra: dict) -> bool:
    return cifra_chart_payload(cifra) is not None


_AWKWARD_ROOT = {"E#": "F", "B#": "C", "Cb": "B", "Fb": "E"}


def _spell_chord_like_cifra(chord: str, target_key: str) -> str:
    """Grafia de acorde igual à cifra (Bb em vez de A#, etc.)."""
    from util import _split_chord_root_quality, format_text_chords_br

    token = (chord or "").strip()
    if not token or token in ("%", "NC", "N.C."):
        return chord
    if token.startswith("*"):
        return chord

    respelled = format_text_chords_br(token, target_key)
    if respelled == token:
        return token

    orig = _split_chord_root_quality(token)
    new = _split_chord_root_quality(respelled)
    if not orig or not new:
        return respelled

    orig_root, _, orig_bass = orig
    new_root, quality, new_bass = new

    natural = _AWKWARD_ROOT.get(new_root)
    if natural and orig_root.upper() == natural:
        new_root = natural

    if new_bass:
        bass_nat = _AWKWARD_ROOT.get(new_bass)
        if bass_nat and (orig_bass or "").upper() == bass_nat:
            new_bass = bass_nat

    out = new_root + quality
    if new_bass:
        out += "/" + new_bass
    return out


def apply_chart_cifra_spelling(chart, target_key: str):
    """Reescreve acordes e tom do chart com as regras de grafia da cifra SetSync."""
    from util import normalize_tom_label

    key = normalize_tom_label(target_key or "")
    if not key:
        return chart

    chart.meta.key = key
    for bar in chart.bars:
        if bar.nav or bar.annotation:
            continue
        grid = bar.get_pulse_grid()
        bar.set_pulse_grid(
            [[_spell_chord_like_cifra(c, key) for c in beat] for beat in grid]
        )
    return chart


def render_cifra_chordsheet_html(
    cifra: dict,
    *,
    semitones: int = 0,
    display_key: str | None = None,
    grade_list: list[dict] | None = None,
    viewer_user_id: str | None = None,
    nashville: bool = False,
) -> str | None:
    """Renderiza HTML do chord sheet no mesmo tom da cifra (tom_original + transposição)."""
    from util import key_at_transpose, normalize_tom_label, normalize_transpose_semitones

    performance = normalize_transpose_semitones(semitones)
    tom_orig = normalize_tom_label(cifra.get("tom_original") or "")
    target_key = display_key or key_at_transpose(tom_orig, performance)

    stored = load_stored_chordsheet(cifra)
    if stored:
        view = apply_private_notes_to_payload(stored, viewer_user_id)
        chart = payload_to_chart(view)
    else:
        payload = cifra_chart_payload(cifra, grade_list=grade_list)
        if not payload:
            return None
        chart = parse_chart(
            payload["source"],
            meta=payload.get("meta"),
            prefs=payload.get("prefs"),
        )
    source_key = normalize_tom_label(chart.meta.key or tom_orig)
    if grade_list is not None:
        # Grade já transposta pelo caller (legado) — só garante o rótulo do tom.
        chart.meta.key = target_key
    else:
        chart_semi, target_key = chordsheet_performance_semitones(
            cifra, performance, chart_source_key=source_key
        )
        if chart_semi:
            chart = transpose_chart(chart, chart_semi, source_key=source_key)
        chart.meta.key = target_key
    apply_chart_cifra_spelling(chart, target_key)
    if nashville:
        _apply_nashville_to_chart(chart)
    return render_chart_html(chart)


def _apply_nashville_to_chart(chart) -> None:
    from chordsheet.nashville import chord_to_nashville

    key = (chart.meta.key or "").strip()
    if not key:
        return
    for bar in chart.bars:
        if bar.nav or bar.blank_spacer or bar.private_note:
            continue
        grid = bar.get_pulse_grid()
        bar.set_pulse_grid(
            [
                [
                    chord_to_nashville(str(c), key)
                    if str(c or "").strip() not in ("", "%", "*", ".")
                    else c
                    for c in beat
                ]
                for beat in grid
            ]
        )


def persist_chordsheet_payload(
    cifra_id: str,
    data: dict[str, Any],
    *,
    user_id: str,
) -> dict[str, Any]:
    """Salva payload chordsheet e sincroniza grade_json."""
    from db import get_cifra, update_cifra

    cifra = get_cifra(cifra_id)
    if not cifra:
        raise ValueError("Cifra não encontrada")

    stored = load_stored_chordsheet(cifra) or {}
    existing_pn = dict(stored.get("private_notes") or {})
    cleaned = extract_and_store_private_notes(data, user_id)
    private_notes = {**existing_pn, **(cleaned.get("private_notes") or {})}

    chart = payload_to_chart(cleaned)
    payload = chart_to_payload(chart, private_notes=private_notes)
    flat = chart_to_grade_flat(chart)
    meta = payload.get("meta") or {}

    bpm_raw = (meta.get("bpm") or "").strip()
    bpm = None
    if bpm_raw:
        try:
            bpm = float(bpm_raw)
        except ValueError:
            pass

    update_cifra(
        cifra_id,
        (meta.get("title") or "").strip() or cifra["titulo"],
        (meta.get("artist") or "").strip() or cifra["artista"],
        (meta.get("key") or "").strip() or cifra["tom_original"],
        cifra["conteudo"],
        cifra.get("cifra_json"),
        json.dumps(flat, ensure_ascii=False) if flat else None,
        json.dumps(payload, ensure_ascii=False),
        bpm if bpm is not None else cifra.get("bpm"),
        cifra.get("duracao_seg"),
    )
    return payload


def extract_chordsheet_source_from_cifra_text(
    cifra_text: str,
    *,
    time_signature: str = "4/4",
) -> str:
    """Monta texto-fonte da grade harmônica a partir de uma cifra com [acordes]."""
    from cifras_tool.calibracao import compassos_com_secoes_da_cifra
    from cifras_tool.compasso import compasso_padrao, parsear_compasso

    text = (cifra_text or "").strip()
    if not text:
        return ""
    info = compasso_padrao()
    if time_signature:
        try:
            parsed = parsear_compasso(time_signature)
            if parsed:
                info = parsed
        except (TypeError, ValueError):
            pass
    compassos = compassos_com_secoes_da_cifra(text, info)
    if not compassos:
        return ""

    lines: list[str] = []
    last_sec: str | None = None
    for comp in compassos:
        sec = (comp.secao or "").strip()
        if sec and sec != last_sec:
            lines.append(f"= {sec}")
            last_sec = sec
        acs = comp.acordes or []
        chord = next(
            (str(a).strip() for a in acs if a and str(a).strip() not in ("%", "")),
            None,
        )
        lines.append(chord if chord else "*")
    return "\n".join(lines)


def extract_chordsheet_from_cifra(cifra: dict, *, time_signature: str = "4/4") -> str:
    """Extrai grade harmônica do conteúdo salvo da cifra."""
    text = _cifra_plain_text_for_extraction(cifra)
    return extract_chordsheet_source_from_cifra_text(text, time_signature=time_signature)


def _cifra_plain_text_for_extraction(cifra: dict) -> str:
    text = (cifra.get("conteudo") or "").strip()
    if text:
        return text
    raw = cifra.get("cifra_json")
    if not raw:
        return ""
    try:
        items = json.loads(raw) if isinstance(raw, str) else raw
    except (json.JSONDecodeError, TypeError):
        return ""
    if not isinstance(items, list):
        return ""
    lines: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        acorde = (item.get("acorde") or "").strip()
        letra = (item.get("texto_letra") or "").strip()
        sec = (item.get("section") or "").strip()
        if sec and (not lines or not lines[-1].startswith("[")):
            lines.append(sec)
        if acorde and letra:
            lines.append(f"[{acorde}]{letra}")
        elif letra:
            lines.append(letra)
        elif acorde:
            lines.append(f"[{acorde}]")
    return "\n".join(lines)
