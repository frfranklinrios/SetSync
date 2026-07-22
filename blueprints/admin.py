import functools
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from blueprints.auth import login_required
from db import (
    is_superadmin,
    get_all_bands,
    get_all_cifras,
    get_all_users,
    get_user,
    get_band_members,
    get_band_cifras,
    get_latest_admin_whatsapp_invites,
    list_band_prospects,
    list_studio_prospects,
    list_testimonials,
    get_testimonial,
    create_testimonial,
    update_testimonial,
    delete_testimonial,
    set_user_superadmin,
    set_user_is_demo,
    is_superadmin_env_only,
)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def superadmin_required(f):
    @functools.wraps(f)
    @login_required
    def wrapped(*args, **kwargs):
        if not is_superadmin(session.get('user_id')):
            flash(
                'Acesso restrito a administradores (configure SETSYNC_SUPERADMIN_* no .env '
                'ou peça promoção no banco).',
                'danger',
            )
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)

    return wrapped


@admin_bp.route('/')
@superadmin_required
def index():
    from models_studio import enrich_studios_for_admin, list_all_studios

    bands = get_all_bands()
    cifras = get_all_cifras()
    users = get_all_users()
    studios = enrich_studios_for_admin(list_all_studios())

    for band in bands:
        owner = get_user(band['owner_id'])
        band['owner'] = owner or {}
        band['members_count'] = len(get_band_members(band['id']))
        band['cifras_count'] = len(get_band_cifras(band['id']))

    from product_funnel import funnel_counts
    from whatsapp_service import is_configured as whatsapp_configured
    from admin_dashboard import build_admin_dashboard_context
    from db import count_user_band_memberships

    admin_ctx = build_admin_dashboard_context()
    funnel_stats = funnel_counts()
    invite_log = get_latest_admin_whatsapp_invites()
    studio_prospects = list_studio_prospects()
    band_prospects = list_band_prospects()

    env_users = os.getenv('SETSYNC_SUPERADMIN_USERNAMES', '').strip()
    env_emails = os.getenv('SETSYNC_SUPERADMIN_EMAILS', '').strip()

    from demo_accounts import is_demo_band, is_demo_heuristic, is_demo_manual, is_demo_user

    for u in users:
        u['is_superadmin_db'] = bool(u.get('is_superadmin'))
        u['is_superadmin_env'] = is_superadmin_env_only(u['id'])
        u['is_env_admin'] = is_superadmin(u['id'])
        u['bands_count'] = count_user_band_memberships(u['id'])
        u['is_demo_manual'] = is_demo_manual(u)
        u['is_demo_auto'] = is_demo_heuristic(u)
        u['is_demo'] = is_demo_user(u)

    for band in bands:
        band['is_demo'] = is_demo_band(band, owner=band.get('owner'))

    for s in studios:
        s['is_demo'] = is_demo_user(s.get('owner'))

    return render_template(
        'admin/index.html',
        bands=bands,
        cifras=cifras,
        users=users,
        studios=studios,
        studio_prospects=studio_prospects,
        band_prospects=band_prospects,
        env_users=env_users,
        env_emails=env_emails,
        funnel_stats=funnel_stats,
        funnel_rows=admin_ctx['funnel_rows'],
        retention=admin_ctx.get('retention') or {},
        metrics_trend=admin_ctx.get('metrics_trend') or {},
        stuck_users=admin_ctx['stuck_users'],
        platform_finance=admin_ctx.get('platform_finance'),
        invite_log=invite_log,
        whatsapp_configured=whatsapp_configured(),
        stats=admin_ctx['stats'],
    )


@admin_bp.route('/api-cifras')
@superadmin_required
def api_cifras():
    from cifras_tool.api_cifras_client import ApiCifrasError, get_api_cifras_report

    report = None
    error = None
    try:
        report = get_api_cifras_report()
    except ApiCifrasError as exc:
        error = str(exc)
    return render_template(
        'admin/api_cifras.html',
        report=report,
        error=error,
    )


@admin_bp.route('/api-cifras/sync', methods=['POST'])
@superadmin_required
def api_cifras_sync():
    from cifras_tool.api_cifras_client import ApiCifrasError, start_api_cifras_sync

    mode = (request.form.get('mode') or 'incremental').strip().lower()
    if mode not in ('incremental', 'full'):
        mode = 'incremental'
    limit_raw = (request.form.get('limit') or '').strip()
    limit = int(limit_raw) if limit_raw.isdigit() else None
    try:
        start_api_cifras_sync(mode=mode, limit=limit)
        try:
            from activity_log import log_activity

            log_activity(
                actor_user_id=session.get('user_id'),
                action='api_cifras_sync_started',
                title='API Cifras — sync',
                summary=f'Sync {mode} iniciado na API de cifras'
                + (f' (limite {limit})' if limit else '')
                + '.',
                entity_type='system',
                url_path='/admin/api-cifras',
            )
        except Exception:
            pass
        flash('Sync da API de cifras iniciado.', 'success')
    except ApiCifrasError as exc:
        flash(str(exc), 'warning' if getattr(exc, 'status_code', None) == 409 else 'danger')
    return redirect(url_for('admin.api_cifras'))


@admin_bp.route('/api-cifras/status.json')
@superadmin_required
def api_cifras_status_json():
    from flask import jsonify
    from cifras_tool.api_cifras_client import ApiCifrasError, get_api_cifras_report

    try:
        return jsonify({'ok': True, 'report': get_api_cifras_report()})
    except ApiCifrasError as exc:
        return jsonify({'ok': False, 'error': str(exc)}), 502


@admin_bp.route('/historico')
@superadmin_required
def historico():
    from activity_log import (
        backfill_admin_activity,
        count_admin_activity,
        count_admin_activity_by_type,
        list_admin_activity,
    )

    backfill_info = backfill_admin_activity()

    page = max(1, int(request.args.get('page') or 1))
    per_page = 50
    entity_type = (request.args.get('tipo') or '').strip() or None
    q = (request.args.get('q') or '').strip() or None
    actor_id = (request.args.get('ator') or '').strip() or None
    total = count_admin_activity(
        entity_type=entity_type, q=q, actor_user_id=actor_id,
    )
    entries = list_admin_activity(
        limit=per_page,
        offset=(page - 1) * per_page,
        entity_type=entity_type,
        q=q,
        actor_user_id=actor_id,
    )
    total_pages = max(1, (total + per_page - 1) // per_page)
    actor = get_user(actor_id) if actor_id else None
    return render_template(
        'admin/historico.html',
        entries=entries,
        page=page,
        total=total,
        total_pages=total_pages,
        per_page=per_page,
        filtro_tipo=entity_type or '',
        filtro_q=q or '',
        filtro_ator=actor_id or '',
        filtro_ator_user=actor,
        counts_by_type=count_admin_activity_by_type(),
        backfill_info=backfill_info,
    )


@admin_bp.route('/usuarios/<user_id>')
@superadmin_required
def usuario_detalhe(user_id):
    """Ficha do usuário + histórico de ações (cadastro, bandas, cifras…)."""
    from activity_log import backfill_admin_activity, count_admin_activity, list_admin_activity
    from db import count_user_band_memberships, get_owned_bands, get_user_bands
    from demo_accounts import is_demo_user

    backfill_admin_activity()
    user = get_user(user_id)
    if not user:
        flash('Usuário não encontrado.', 'warning')
        return redirect(url_for('admin.index') + '#tab-users')

    user['bands_count'] = count_user_band_memberships(user_id)
    user['is_demo'] = is_demo_user(user)
    user['is_superadmin_db'] = bool(user.get('is_superadmin'))
    user['is_env_admin'] = is_superadmin(user_id)

    owned = get_owned_bands(user_id)
    member_of = get_user_bands(user_id)
    entries = list_admin_activity(limit=100, related_user_id=user_id)

    return render_template(
        'admin/usuario.html',
        user=user,
        owned_bands=owned,
        member_bands=member_of,
        entries=entries,
        activity_total=count_admin_activity(related_user_id=user_id),
    )


@admin_bp.route('/depoimentos')
@superadmin_required
def depoimentos():
    return render_template(
        'admin/depoimentos.html',
        testimonials=list_testimonials(active_only=False),
    )


@admin_bp.route('/depoimentos/criar', methods=['GET', 'POST'])
@superadmin_required
def depoimentos_criar():
    if request.method == 'POST':
        data = {
            'nome': request.form.get('nome', '').strip(),
            'cidade': request.form.get('cidade', '').strip(),
            'descricao': request.form.get('descricao', '').strip(),
            'texto': request.form.get('texto', '').strip(),
            'foto_url': request.form.get('foto_url', '').strip(),
            'ativo': request.form.get('ativo') == '1',
            'ordem': int(request.form.get('ordem') or 0),
        }
        if not data['nome'] or not data['texto']:
            flash('Nome e texto são obrigatórios.', 'danger')
        else:
            create_testimonial(data)
            try:
                from activity_log import log_activity

                log_activity(
                    actor_user_id=session.get('user_id'),
                    action='testimonial_created',
                    title='Depoimento criado',
                    summary=f'Depoimento de «{data.get("nome") or "sem nome"}» criado.',
                    entity_type='testimonial',
                    url_path='/admin/depoimentos',
                )
            except Exception:
                pass
            flash('Depoimento criado.', 'success')
            return redirect(url_for('admin.depoimentos'))
    return render_template('admin/depoimento_form.html', testimonial=None)


@admin_bp.route('/depoimentos/<int:testimonial_id>/editar', methods=['GET', 'POST'])
@superadmin_required
def depoimentos_editar(testimonial_id: int):
    t = get_testimonial(testimonial_id)
    if not t:
        flash('Depoimento não encontrado.', 'danger')
        return redirect(url_for('admin.depoimentos'))
    if request.method == 'POST':
        data = {
            'nome': request.form.get('nome', '').strip(),
            'cidade': request.form.get('cidade', '').strip(),
            'descricao': request.form.get('descricao', '').strip(),
            'texto': request.form.get('texto', '').strip(),
            'foto_url': request.form.get('foto_url', '').strip(),
            'ativo': request.form.get('ativo') == '1',
            'ordem': int(request.form.get('ordem') or 0),
        }
        update_testimonial(testimonial_id, data)
        try:
            from activity_log import log_activity

            log_activity(
                actor_user_id=session.get('user_id'),
                action='testimonial_updated',
                title='Depoimento atualizado',
                summary=f'Depoimento de «{data.get("nome") or "sem nome"}» atualizado.',
                entity_type='testimonial',
                entity_id=str(testimonial_id),
                url_path='/admin/depoimentos',
            )
        except Exception:
            pass
        flash('Depoimento atualizado.', 'success')
        return redirect(url_for('admin.depoimentos'))
    return render_template('admin/depoimento_form.html', testimonial=t)


@admin_bp.route('/depoimentos/<int:testimonial_id>/excluir', methods=['POST'])
@superadmin_required
def depoimentos_excluir(testimonial_id: int):
    t = get_testimonial(testimonial_id)
    delete_testimonial(testimonial_id)
    try:
        from activity_log import log_activity

        log_activity(
            actor_user_id=session.get('user_id'),
            action='testimonial_deleted',
            title='Depoimento removido',
            summary=f'Depoimento «{(t or {}).get("nome") or testimonial_id}» removido.',
            entity_type='testimonial',
            entity_id=str(testimonial_id),
            url_path='/admin/depoimentos',
        )
    except Exception:
        pass
    flash('Depoimento removido.', 'success')
    return redirect(url_for('admin.depoimentos'))


@admin_bp.route('/convite-whatsapp', methods=['POST'])
@superadmin_required
def convite_whatsapp():
    target_type = (request.form.get('target_type') or '').strip().lower()
    target_id = (request.form.get('target_id') or '').strip()
    phone = (request.form.get('phone') or '').strip()
    action = (request.form.get('action') or 'send').strip()

    if action == 'resend' and target_id and target_type in ('band_prospect', 'studio_prospect'):
        from admin_outreach import resend_prospect_invite

        result = resend_prospect_invite(
            target_type=target_type,
            target_id=target_id,
            sent_by_user_id=session['user_id'],
        )
        if result.get('ok'):
            flash('Convite reenviado por WhatsApp.', 'success')
        else:
            flash(result.get('error') or 'Não foi possível enviar.', 'danger')
        return redirect(url_for('admin.index') + '#tab-convites')

    if target_type == 'studio_prospect':
        from admin_outreach import send_studio_prospect_invite

        result = send_studio_prospect_invite(
            phone=phone,
            nome=(request.form.get('studio_nome') or request.form.get('prospect_nome') or '').strip(),
            cidade=(request.form.get('studio_cidade') or request.form.get('prospect_cidade') or '').strip(),
            sent_by_user_id=session['user_id'],
            notes=(request.form.get('notes') or '').strip(),
        )
    elif target_type == 'band_prospect':
        from admin_outreach import send_band_prospect_invite

        result = send_band_prospect_invite(
            phone=phone,
            nome=(request.form.get('band_nome') or request.form.get('prospect_nome') or '').strip(),
            cidade=(request.form.get('band_cidade') or request.form.get('prospect_cidade') or '').strip(),
            sent_by_user_id=session['user_id'],
            notes=(request.form.get('notes') or '').strip(),
        )
    else:
        flash('Tipo de convite inválido.', 'danger')
        return redirect(url_for('admin.index') + '#admin-convites')

    if result.get('ok'):
        flash('Convite de cadastro enviado por WhatsApp.', 'success')
    else:
        flash(result.get('error') or 'Não foi possível enviar.', 'danger')
    return redirect(url_for('admin.index') + '#admin-convites')


@admin_bp.route('/usuarios/<user_id>/superadmin', methods=['POST'])
@superadmin_required
def toggle_superadmin(user_id: str):
    enabled = request.form.get('enabled') == '1'
    target = get_user(user_id)
    if set_user_superadmin(user_id, enabled):
        try:
            from activity_log import log_activity
            from db import user_display_name

            nome = user_display_name(target) if target else user_id
            estado = 'concedido' if enabled else 'revogado'
            log_activity(
                actor_user_id=session.get('user_id'),
                action='superadmin_toggled',
                title='Superadmin',
                summary=f'Privilégio de superadmin {estado} para {nome}.',
                entity_type='user',
                entity_id=user_id,
                url_path='/admin/#tab-users',
            )
        except Exception:
            pass
        flash('Privilégio de superadmin do app atualizado.', 'success')
    else:
        flash('Usuário não encontrado.', 'danger')
    return redirect(url_for('admin.index') + '#tab-users')


@admin_bp.route('/usuarios/<user_id>/entrar', methods=['POST'])
@superadmin_required
def impersonate_user(user_id: str):
    """Master assume a sessão do usuário para ver o app como ele."""
    from blueprints.auth import is_impersonating, start_impersonation
    from db import user_display_name

    if is_impersonating():
        flash('Já está como outro usuário. Volte ao master antes de entrar em outra conta.', 'warning')
        return redirect(url_for('dashboard'))

    master_id = session.get('user_id')
    if not master_id or user_id == master_id:
        flash('Não é possível entrar na própria conta.', 'warning')
        return redirect(url_for('admin.usuario_detalhe', user_id=user_id))

    target = get_user(user_id)
    if not target:
        flash('Usuário não encontrado.', 'warning')
        return redirect(url_for('admin.index') + '#tab-users')

    start_impersonation(target, impersonator_id=master_id)
    try:
        from activity_log import log_activity

        log_activity(
            actor_user_id=master_id,
            action='user_impersonated',
            title='Entrar como usuário',
            summary=(
                f'Master entrou como {user_display_name(target)} '
                f'(@{target.get("username") or ""}).'
            ),
            entity_type='user',
            entity_id=user_id,
            url_path=f'/admin/usuarios/{user_id}',
        )
    except Exception:
        pass

    flash(
        f'Você está vendo o app como {user_display_name(target)}. '
        'Use “Voltar ao master” na barra amarela para sair.',
        'info',
    )
    return redirect(url_for('dashboard'))


@admin_bp.route('/impersonate/parar', methods=['POST'])
@login_required
def stop_impersonate():
    """Sai da sessão do usuário e volta para o master."""
    from blueprints.auth import stop_impersonation

    master = stop_impersonation()
    if not master:
        flash('Nenhuma sessão de master para restaurar.', 'warning')
        return redirect(url_for('dashboard'))
    flash('Voltou à conta master.', 'success')
    return redirect(url_for('admin.index') + '#tab-users')


@admin_bp.route('/usuarios/<user_id>/demo', methods=['POST'])
@superadmin_required
def toggle_user_demo(user_id: str):
    enabled = request.form.get('enabled') == '1'
    target = get_user(user_id)
    if not target:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('admin.index') + '#tab-users')
    if set_user_is_demo(user_id, enabled):
        try:
            from activity_log import log_activity
            from db import user_display_name

            nome = user_display_name(target)
            estado = 'marcada como teste/demo' if enabled else 'desmarcada como teste'
            log_activity(
                actor_user_id=session.get('user_id'),
                action='user_demo_toggled',
                title='Conta teste',
                summary=f'Conta {nome} {estado}.',
                entity_type='user',
                entity_id=user_id,
                url_path='/admin/#tab-users',
            )
        except Exception:
            pass
        if enabled:
            flash('Conta marcada como teste (Demo).', 'success')
        else:
            from demo_accounts import is_demo_heuristic

            refreshed = get_user(user_id) or target
            if is_demo_heuristic(refreshed):
                flash(
                    'Flag manual removida, mas a conta ainda conta como Demo '
                    '(username/e-mail showcase ou lista do .env).',
                    'warning',
                )
            else:
                flash('Marcação de teste removida.', 'success')
    else:
        flash('Não foi possível atualizar a conta.', 'danger')
    return redirect(url_for('admin.index') + '#tab-users')
