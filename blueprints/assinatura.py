"""Assinaturas, Mercado Pago e vouchers."""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from blueprints.auth import login_required
from blueprints.admin import superadmin_required
from db import (
    create_voucher,
    get_assinatura,
    get_assinatura_by_mp_id,
    get_band,
    get_owned_bands,
    get_user,
    list_voucher_usos,
    list_vouchers,
    set_voucher_ativo,
    update_assinatura,
)
from mercadopago_client import (
    build_preapproval_checkout_body,
    checkout_init_point,
    get_mp_sdk,
    mp_config_status,
    mp_error_message,
)
from monetizacao import PLANOS, PLANO_INDIVIDUAL, PLANO_PRO, PLANO_WORSHIP, planos_para_site
from monetizacao import (
    PLANO_ESTUDIO_PREMIUM,
    PLANO_ESTUDIO_BASICO,
    PLANOS_ESTUDIO,
    planos_estudio_para_site,
    studio_plano_badge_ui,
)
from mp_webhook import (
    ativar_assinatura_mp,
    extrair_topic_id,
    processar_notificacao_mp,
    webhook_autentico,
)
from security import external_url_for
from vouchers import (
    VOUCHER_INDICACAO_DIAS,
    VOUCHER_DESTINO_ESTUDIO,
    criar_voucher_indicacao,
    criar_voucher_indicacao_estudio,
    gerar_codigo_voucher,
    resgatar_voucher,
    resgatar_voucher_estudio,
    voucher_destino,
)

assinatura_bp = Blueprint('assinatura_bp', __name__)


def _user_email(user_id: str) -> str:
    user = get_user(user_id)
    return (user or {}).get('email') or ''


def _banda_do_usuario(banda_id: str, user_id: str) -> dict | None:
    band = get_band(banda_id)
    if not band or band['owner_id'] != user_id:
        return None
    return band


def _mp_notification_url() -> str:
    """URL de webhook; inclui ?secret= quando MP_WEBHOOK_SECRET está definido."""
    url = external_url_for('assinatura_bp.webhook')
    secret = (os.getenv('MP_WEBHOOK_SECRET') or '').strip()
    if not secret:
        return url
    sep = '&' if '?' in url else '?'
    return f'{url}{sep}secret={secret}'


@assinatura_bp.route('/planos')
def planos_redirect():
    """Atalho legado usado em guias SEO e conteúdo antigo."""
    return redirect(url_for('assinatura_bp.planos'), code=301)


@assinatura_bp.route('/assinatura/planos')
@login_required
def planos():
    """Página com planos e resgate de voucher."""
    user_id = session['user_id']
    bandas = get_owned_bands(user_id)
    banda_id = request.args.get('banda_id') or (bandas[0]['id'] if bandas else None)
    from monetizacao import get_assinatura_banda, plano_badge_ui
    assinatura = get_assinatura_banda(banda_id) if banda_id else None
    plano_ui = plano_badge_ui(banda_id) if banda_id else None
    mp_status = mp_config_status()
    from models_studio import list_studios_by_owner
    tem_estudio = bool(list_studios_by_owner(user_id))
    return render_template(
        'assinatura/planos.html',
        planos=PLANOS,
        planos_estudio=planos_estudio_para_site(),
        studio_plano_ui=studio_plano_badge_ui(user_id),
        bandas=bandas,
        banda_id=banda_id,
        tem_estudio=tem_estudio,
        assinatura=assinatura.to_dict() if assinatura else None,
        plano_ui=plano_ui,
        mp_status=mp_status,
    )


@assinatura_bp.route('/assinatura/iniciar/<plano>', methods=['POST'])
@login_required
def iniciar(plano):
    """Cria assinatura recorrente no MP e redireciona ao Checkout."""
    if plano not in (PLANO_INDIVIDUAL, PLANO_PRO, PLANO_WORSHIP):
        flash('Plano inválido', 'danger')
        return redirect(url_for('assinatura_bp.planos'))

    banda_id = request.form.get('banda_id', '').strip()
    band = _banda_do_usuario(banda_id, session['user_id'])
    if not band:
        flash('Selecione uma banda da qual você é dona/dono', 'danger')
        return redirect(url_for('assinatura_bp.planos'))

    email = _user_email(session['user_id'])
    if not email:
        flash('Cadastre um e-mail na sua conta para assinar', 'danger')
        return redirect(url_for('assinatura_bp.planos'))

    mp_status = mp_config_status()
    if not mp_status['pronto_checkout']:
        flash('Mercado Pago não configurado: ' + ' · '.join(mp_status['faltando']), 'warning')
        return redirect(url_for('assinatura_bp.planos', banda_id=banda_id))

    try:
        sdk = get_mp_sdk()
        preapproval_data = build_preapproval_checkout_body(
            plano,
            payer_email=email,
            back_url=external_url_for('assinatura_bp.sucesso'),
            external_reference=f'{banda_id}:{plano}',
            reason=f'Uníssono {PLANOS[plano].nome} — Banda: {band["name"]}',
            billing_period=request.form.get('billing_period', 'monthly'),
            notification_url=_mp_notification_url(),
        )
        result = sdk.preapproval().create(preapproval_data)
        if result.get('status') not in (200, 201):
            current_app.logger.error('MP preapproval: %s', result)
            detalhe = mp_error_message(result)
            flash(
                f'Não foi possível iniciar o checkout. {detalhe}',
                'danger',
            )
            return redirect(url_for('assinatura_bp.planos', banda_id=banda_id))

        init_point = checkout_init_point(result)
        if not init_point:
            flash('URL de checkout não retornada pelo Mercado Pago', 'danger')
            return redirect(url_for('assinatura_bp.planos', banda_id=banda_id))

        session['mp_checkout'] = {'banda_id': banda_id, 'plano': plano}
        mp_id = (result.get('response') or {}).get('id')
        if mp_id:
            update_assinatura(banda_id, mp_preapproval_id=mp_id)
            session['mp_checkout']['preapproval_id'] = str(mp_id)
        return redirect(init_point)
    except Exception as exc:
        current_app.logger.exception('Erro ao iniciar assinatura: %s', exc)
        flash(f'Erro ao conectar ao Mercado Pago: {exc}', 'danger')
        return redirect(url_for('assinatura_bp.planos', banda_id=banda_id))


@assinatura_bp.route('/assinatura/estudio/iniciar/<plano>', methods=['POST'])
@login_required
def iniciar_estudio(plano):
    """Checkout Mercado Pago para plano Estúdio Premium (por conta do dono)."""
    if plano not in PLANOS_ESTUDIO or plano != PLANO_ESTUDIO_PREMIUM:
        flash('Plano de estúdio inválido', 'danger')
        return redirect(url_for('assinatura_bp.planos') + '#estudio')

    user_id = session['user_id']
    email = _user_email(user_id)
    if not email:
        flash('Cadastre um e-mail na sua conta para assinar', 'danger')
        return redirect(url_for('assinatura_bp.planos') + '#estudio')

    mp_status = mp_config_status()
    if not mp_status.get('pronto_checkout_estudio'):
        flash('Mercado Pago não configurado: ' + ' · '.join(mp_status['faltando']), 'warning')
        return redirect(url_for('assinatura_bp.planos') + '#estudio')

    try:
        from models_studio import update_studio_subscription

        sdk = get_mp_sdk()
        definicao = PLANOS_ESTUDIO[plano]
        preapproval_data = build_preapproval_checkout_body(
            plano,
            payer_email=email,
            back_url=external_url_for('assinatura_bp.sucesso_estudio'),
            external_reference=f'studio:{user_id}:{plano}',
            reason=f'Uníssono {definicao.nome}',
            billing_period=request.form.get('billing_period', 'monthly'),
            notification_url=_mp_notification_url(),
        )
        result = sdk.preapproval().create(preapproval_data)
        if result.get('status') not in (200, 201):
            current_app.logger.error('MP preapproval estúdio: %s', result)
            flash(f'Não foi possível iniciar o checkout. {mp_error_message(result)}', 'danger')
            return redirect(url_for('assinatura_bp.planos') + '#estudio')

        init_point = checkout_init_point(result)
        if not init_point:
            flash('URL de checkout não retornada pelo Mercado Pago', 'danger')
            return redirect(url_for('assinatura_bp.planos') + '#estudio')

        session['mp_checkout'] = {'tipo': 'studio', 'user_id': user_id, 'plano': plano}
        mp_id = (result.get('response') or {}).get('id')
        if mp_id:
            update_studio_subscription(user_id, mp_preapproval_id=mp_id)
            session['mp_checkout']['preapproval_id'] = str(mp_id)
        return redirect(init_point)
    except Exception as exc:
        current_app.logger.exception('Erro ao iniciar assinatura estúdio: %s', exc)
        flash(f'Erro ao conectar ao Mercado Pago: {exc}', 'danger')
        return redirect(url_for('assinatura_bp.planos') + '#estudio')


@assinatura_bp.route('/assinatura/estudio/sucesso')
@login_required
def sucesso_estudio():
    """Retorno do MP após checkout do plano Estúdio."""
    from models_studio import get_or_create_studio_subscription
    from mp_webhook import ativar_studio_subscription_mp

    status_retorno = (request.args.get('status') or request.args.get('collection_status') or '').lower()
    checkout = session.get('mp_checkout') or {}
    user_id = session['user_id']
    plano = PLANO_ESTUDIO_PREMIUM
    if checkout.get('tipo') == 'studio':
        user_id = checkout.get('user_id', user_id)
        plano = checkout.get('plano', plano)

    if user_id != session['user_id']:
        flash('Sem permissão para ativar este plano.', 'danger')
        return redirect(url_for('assinatura_bp.planos') + '#estudio')

    if status_retorno in ('failure', 'rejected', 'null'):
        flash('Pagamento não aprovado. Tente novamente.', 'danger')
        return redirect(url_for('assinatura_bp.planos') + '#estudio')

    preapproval_id = (checkout.get('preapproval_id') or request.args.get('preapproval_id') or '').strip()
    if not preapproval_id:
        row = get_or_create_studio_subscription(user_id)
        preapproval_id = (row.get('mp_preapproval_id') or '').strip()

    if preapproval_id:
        try:
            sdk = get_mp_sdk()
            info = sdk.preapproval().get(preapproval_id)
            body = info.get('response') or {}
            ref = body.get('external_reference', '')
            if ref.startswith('studio:'):
                parts = ref.split(':', 2)
                if len(parts) >= 3:
                    plano = parts[2]
            status_mp = (body.get('status') or '').lower()
            if status_mp in ('authorized', 'active', 'approved'):
                next_charge = body.get('next_payment_date')
                ativar_studio_subscription_mp(user_id, plano, preapproval_id, next_charge)
                from product_funnel import log_funnel_step
                from google_ads import mark_funnel_event
                log_funnel_step(user_id, 'assinatura_paga', meta={'plano': plano, 'tipo': 'studio'})
                mark_funnel_event('assinatura_paga')
                session.pop('mp_checkout', None)
                flash('Plano Estúdio Premium ativado!', 'success')
            else:
                flash(
                    'Pagamento em processamento (PIX/cartão). Assim que o Mercado Pago confirmar, '
                    'o Premium libera automaticamente.',
                    'info',
                )
        except Exception as exc:
            current_app.logger.exception('Erro ao confirmar sucesso MP estúdio: %s', exc)
            flash('Checkout concluído. Aguarde a confirmação automática.', 'info')
    else:
        flash('Assinatura registrada. Aguarde a confirmação.', 'info')

    return redirect(url_for('assinatura_bp.planos') + '#estudio')


def _resolve_band_preapproval_id(banda_id: str | None, checkout: dict | None) -> str | None:
    """ID real de preapproval (nunca payment_id/collection_id)."""
    pid = None
    if checkout:
        pid = (checkout.get('preapproval_id') or '').strip() or None
    if not pid:
        pid = (request.args.get('preapproval_id') or '').strip() or None
    if not pid and banda_id:
        row = get_assinatura(banda_id)
        pid = ((row or {}).get('mp_preapproval_id') or '').strip() or None
    return pid


def _try_activate_band_preapproval(banda_id: str, plano: str, preapproval_id: str) -> str:
    """
    Consulta MP e tenta ativar. Retorna: 'ativa' | 'pendente' | 'erro'.
    """
    try:
        sdk = get_mp_sdk()
        info = sdk.preapproval().get(preapproval_id)
        if info.get('status') not in (200, 201):
            return 'erro'
        body = info.get('response') or {}
        ref = body.get('external_reference', '')
        if ':' in ref and not str(ref).startswith('studio:'):
            banda_id, plano = ref.split(':', 1)
        status_mp = (body.get('status') or '').lower()
        if status_mp in ('authorized', 'active', 'approved'):
            next_charge = body.get('next_payment_date') or body.get('auto_recurring', {}).get('end_date')
            ativar_assinatura_mp(banda_id, plano, preapproval_id, next_charge)
            try:
                from product_funnel import log_funnel_step
                from google_ads import mark_funnel_event
                log_funnel_step(session['user_id'], 'assinatura_paga', meta={'plano': plano})
                mark_funnel_event('assinatura_paga')
            except Exception:
                pass
            try:
                import admin_notifications as an
                an.subscription_activated(banda_id, plano, source='checkout')
            except Exception:
                current_app.logger.exception('Notificação admin (sucesso checkout) falhou')
            return 'ativa'
        return 'pendente'
    except Exception as exc:
        current_app.logger.exception('Erro ao confirmar preapproval: %s', exc)
        return 'erro'


@assinatura_bp.route('/assinatura/sucesso')
@login_required
def sucesso():
    """Retorno do MP após checkout de assinatura."""
    status_retorno = (request.args.get('status') or request.args.get('collection_status') or '').lower()
    checkout = session.get('mp_checkout') or {}
    if checkout.get('tipo') == 'studio':
        return redirect(url_for('assinatura_bp.sucesso_estudio', **request.args))

    banda_id = checkout.get('banda_id') or request.args.get('banda_id')
    plano = checkout.get('plano') or PLANO_PRO

    if status_retorno == 'pending':
        return redirect(url_for(
            'assinatura_bp.pendente',
            banda_id=banda_id or '',
            plano=plano,
        ))
    if status_retorno in ('failure', 'rejected', 'null'):
        return redirect(url_for(
            'assinatura_bp.falha',
            banda_id=banda_id or '',
            plano=plano,
        ))

    if not banda_id and checkout.get('preapproval_id'):
        row = get_assinatura_by_mp_id(checkout['preapproval_id'])
        if row:
            banda_id = row['banda_id']
            if row.get('plano') and row['plano'] != 'gratis':
                plano = row['plano']

    preapproval_id = _resolve_band_preapproval_id(banda_id, checkout)

    if preapproval_id and banda_id:
        band = get_band(banda_id)
        if not band or band['owner_id'] != session['user_id']:
            flash('Sem permissão para ativar plano desta banda.', 'danger')
            return redirect(url_for('assinatura_bp.planos'))
        resultado = _try_activate_band_preapproval(banda_id, plano, preapproval_id)
        if resultado == 'ativa':
            session.pop('mp_checkout', None)
            flash('Assinatura ativada com sucesso!', 'success')
            return redirect(url_for('assinatura_bp.planos', banda_id=banda_id))
        if resultado == 'pendente':
            return redirect(url_for(
                'assinatura_bp.pendente',
                banda_id=banda_id,
                plano=plano,
            ))

    flash('Assinatura registrada. Confirmando pagamento…', 'info')
    return redirect(url_for(
        'assinatura_bp.pendente',
        banda_id=banda_id or '',
        plano=plano,
    ))


@assinatura_bp.route('/assinatura/pendente')
@login_required
def pendente():
    checkout = session.get('mp_checkout') or {}
    banda_id = request.args.get('banda_id') or checkout.get('banda_id') or ''
    plano = request.args.get('plano') or checkout.get('plano') or PLANO_PRO
    band = get_band(banda_id) if banda_id else None
    if band and band['owner_id'] != session['user_id']:
        band = None
        banda_id = ''
    return render_template(
        'assinatura/pendente.html',
        banda_id=banda_id,
        plano=plano,
        band=band,
        plano_nome=(PLANOS.get(plano).nome if plano in PLANOS else plano),
    )


@assinatura_bp.route('/assinatura/falha')
@login_required
def falha():
    checkout = session.get('mp_checkout') or {}
    banda_id = request.args.get('banda_id') or checkout.get('banda_id') or ''
    plano = request.args.get('plano') or checkout.get('plano') or PLANO_PRO
    band = get_band(banda_id) if banda_id else None
    if band and band['owner_id'] != session['user_id']:
        band = None
        banda_id = ''
    return render_template(
        'assinatura/falha.html',
        banda_id=banda_id,
        plano=plano,
        band=band,
        plano_nome=(PLANOS.get(plano).nome if plano in PLANOS else plano),
    )


@assinatura_bp.route('/assinatura/status.json')
@login_required
def status_json():
    """Polling leve após PIX/boleto/cartão pendente."""
    checkout = session.get('mp_checkout') or {}
    banda_id = request.args.get('banda_id') or checkout.get('banda_id')
    if not banda_id:
        return jsonify({'ok': False, 'status': 'unknown'}), 400
    band = get_band(banda_id)
    if not band or band['owner_id'] != session['user_id']:
        return jsonify({'ok': False, 'status': 'forbidden'}), 403

    row = get_assinatura(banda_id) or {}
    if (row.get('status') or '').lower() == 'ativa' and (row.get('plano') or '') not in ('', 'gratis'):
        session.pop('mp_checkout', None)
        return jsonify({
            'ok': True,
            'status': 'ativa',
            'plano': row.get('plano'),
            'redirect': url_for('assinatura_bp.planos', banda_id=banda_id),
        })

    preapproval_id = _resolve_band_preapproval_id(banda_id, checkout)
    plano = checkout.get('plano') or row.get('plano') or PLANO_PRO
    if preapproval_id:
        resultado = _try_activate_band_preapproval(banda_id, plano, preapproval_id)
        if resultado == 'ativa':
            session.pop('mp_checkout', None)
            return jsonify({
                'ok': True,
                'status': 'ativa',
                'plano': plano,
                'redirect': url_for('assinatura_bp.planos', banda_id=banda_id),
            })
        return jsonify({'ok': True, 'status': resultado})

    return jsonify({'ok': True, 'status': 'pendente'})


@assinatura_bp.route('/assinatura/webhook', methods=['POST', 'GET'])
def webhook():
    """Notificações do Mercado Pago (IPN / Webhooks v2)."""
    secret = os.getenv('MP_WEBHOOK_SECRET', '')
    if not webhook_autentico(request, secret):
        current_app.logger.warning('Webhook MP rejeitado (assinatura inválida)')
        return '', 401

    topic, data_id = extrair_topic_id(request)
    current_app.logger.info(
        'Webhook MP recebido topic=%s id=%s args=%s',
        topic,
        data_id,
        dict(request.args),
    )

    try:
        processar_notificacao_mp(topic, data_id)
    except Exception as exc:
        current_app.logger.exception('Erro no webhook MP: %s', exc)
        return '', 500

    return '', 200


@assinatura_bp.route('/voucher/resgatar', methods=['POST'])
@login_required
def voucher_resgatar():
    """Resgata voucher via AJAX (banda ou estúdio)."""
    data = request.get_json(silent=True) or request.form
    codigo = (data.get('codigo') or '').strip()
    if not codigo:
        return jsonify({'ok': False, 'erro': 'Informe o código'}), 400

    from db import get_voucher_by_codigo, get_user

    voucher = get_voucher_by_codigo(codigo)
    if not voucher:
        return jsonify({'ok': False, 'erro': 'Voucher não encontrado'}), 400

    user = get_user(session['user_id']) or {}
    user_nome = user.get('name') or 'Usuário'

    if voucher_destino(voucher) == VOUCHER_DESTINO_ESTUDIO:
        ok, msg, info = resgatar_voucher_estudio(codigo, session['user_id'], user_nome)
        if not ok:
            return jsonify({'ok': False, 'erro': msg}), 400
        return jsonify({'ok': True, 'mensagem': msg, 'info': info})

    banda_id = (data.get('banda_id') or '').strip()
    band = _banda_do_usuario(banda_id, session['user_id'])
    if not band:
        return jsonify({'ok': False, 'erro': 'Selecione uma banda válida'}), 400
    ok, msg, info = resgatar_voucher(codigo, banda_id, band['name'])
    if not ok:
        return jsonify({'ok': False, 'erro': msg}), 400
    import admin_notifications as an
    an.voucher_redeemed(
        banda_id,
        session['user_id'],
        codigo.upper(),
        (info or {}).get('plano_nome', 'Pro'),
        int((info or {}).get('dias') or 0) if not (info or {}).get('vitalicio') else 0,
    )
    return jsonify({'ok': True, 'mensagem': msg, 'info': info})


@assinatura_bp.route('/voucher/indicar', methods=['GET', 'POST'])
@login_required
def voucher_indicar():
    """Página para gerar voucher de indicação (banda ou estúdio)."""
    codigo, erro, tipo = None, None, None
    if request.method == 'POST':
        tipo = (request.form.get('tipo') or 'banda').strip().lower()
        if tipo == 'estudio':
            codigo, erro = criar_voucher_indicacao_estudio(session['user_id'])
        else:
            tipo = 'banda'
            codigo, erro = criar_voucher_indicacao(session['user_id'])
    from security import external_url_for

    return render_template(
        'assinatura/indicar.html',
        codigo=codigo,
        erro=erro,
        tipo=tipo,
        dias_indicacao=VOUCHER_INDICACAO_DIAS,
        meses_indicacao=max(1, VOUCHER_INDICACAO_DIAS // 30),
        site_url=external_url_for('index'),
    )


@assinatura_bp.route('/admin/vouchers')
@superadmin_required
def admin_vouchers():
    vouchers = list_vouchers()
    for v in vouchers:
        v['criador'] = get_user(v['criado_por_id']) if v.get('criado_por_id') else None
    return render_template('admin/vouchers.html', vouchers=vouchers)


@assinatura_bp.route('/admin/vouchers/criar', methods=['POST'])
@superadmin_required
def admin_vouchers_criar():
    destino = (request.form.get('destino') or 'banda').strip().lower()
    plano = request.form.get('plano', PLANO_PRO)
    if destino == VOUCHER_DESTINO_ESTUDIO:
        if plano != PLANO_ESTUDIO_PREMIUM:
            flash('Para estúdio, use o plano Estúdio Premium', 'danger')
            return redirect(url_for('assinatura_bp.admin_vouchers'))
    elif plano not in (PLANO_INDIVIDUAL, PLANO_PRO, PLANO_WORSHIP):
        flash('Plano inválido', 'danger')
        return redirect(url_for('assinatura_bp.admin_vouchers'))
    eh_vitalicio = request.form.get('eh_vitalicio') in ('1', 'on', 'true')
    dias = 0 if eh_vitalicio else int(request.form.get('dias', 30))
    if not eh_vitalicio and dias < 1:
        flash('Informe a quantidade de dias ou marque vitalício', 'danger')
        return redirect(url_for('assinatura_bp.admin_vouchers'))
    max_usos = request.form.get('max_usos', '').strip()
    max_usos_int = int(max_usos) if max_usos else None
    prefixo = request.form.get('prefixo', '').strip() or None
    if destino == VOUCHER_DESTINO_ESTUDIO and not prefixo:
        prefixo = 'ESTUDIO'
    data_exp = request.form.get('data_expiracao', '').strip() or None
    codigo = gerar_codigo_voucher(prefixo)
    create_voucher(
        codigo=codigo,
        plano=plano,
        dias=dias,
        criado_por_id=session['user_id'],
        max_usos=max_usos_int,
        data_expiracao=data_exp,
        eh_vitalicio=eh_vitalicio,
        destino=destino,
    )
    tipo = 'vitalício' if eh_vitalicio else f'{dias} dias'
    alvo = 'estúdio' if destino == VOUCHER_DESTINO_ESTUDIO else 'banda'
    flash(f'Voucher {codigo} criado ({tipo}, {alvo})!', 'success')
    return redirect(url_for('assinatura_bp.admin_vouchers'))


@assinatura_bp.route('/admin/vouchers/<codigo>/desativar', methods=['POST'])
@superadmin_required
def admin_vouchers_desativar(codigo):
    if set_voucher_ativo(codigo, False):
        flash(f'Voucher {codigo} desativado.', 'success')
    else:
        flash('Voucher não encontrado', 'danger')
    return redirect(url_for('assinatura_bp.admin_vouchers'))


@assinatura_bp.route('/admin/vouchers/<codigo>/usos')
@superadmin_required
def admin_vouchers_usos(codigo):
    from db import get_voucher_by_codigo, list_studio_voucher_usos
    voucher = get_voucher_by_codigo(codigo)
    if not voucher:
        return jsonify({'usos': []}), 404
    if voucher_destino(voucher) == VOUCHER_DESTINO_ESTUDIO:
        usos = list_studio_voucher_usos(voucher['id'])
        for u in usos:
            u['banda_nome'] = u.get('user_nome') or u.get('user_id')
    else:
        usos = list_voucher_usos(voucher['id'])
    return jsonify({'usos': usos})


@assinatura_bp.route('/bandas')
def bandas():
    """Landing page para bandas e músicos."""
    from cifras_tool.api_cifras_client import get_api_cifras_public_stats
    from db import count_bands, count_cifras, count_setlists, list_testimonials
    from monetizacao import planos_para_site

    stats = {
        'bandas': count_bands(),
        'musicas': count_cifras(),
        'setlists': count_setlists(),
    }
    api_cifras_stats = get_api_cifras_public_stats()
    if api_cifras_stats.get('available'):
        stats['biblioteca'] = True

    return render_template(
        'bandas.html',
        planos_site=planos_para_site(),
        stats=stats,
        testimonials=list_testimonials(active_only=True),
    )


@assinatura_bp.route('/igrejas')
def igrejas():
    """Landing page para igrejas."""
    from config import whatsapp_number, whatsapp_message
    from monetizacao import plano_worship_para_site, PLANOS
    from db import list_testimonials

    return render_template(
        'igrejas.html',
        plano_worship=plano_worship_para_site(),
        plano_pro={'preco_mensal': PLANOS['pro'].preco_mensal, 'nome': PLANOS['pro'].nome},
        worship_mensal=PLANOS['worship'].preco_mensal,
        testimonials=list_testimonials(active_only=True),
        whatsapp=whatsapp_number(),
        whatsapp_message=whatsapp_message(),
    )
