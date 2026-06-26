from flask import Flask, render_template, redirect, url_for, session, send_from_directory, make_response, request, flash, jsonify
from werkzeug.exceptions import HTTPException
from config import config
from blueprints.auth import auth_bp, login_required
from blueprints.bands import bands_bp
from blueprints.legal import legal_bp
from blueprints.cifras import cifras_bp
from blueprints.setlists import setlists_bp
from blueprints.cifras_import import cifras_import_bp
from blueprints.ajuda import ajuda_bp
from blueprints.roadmap import roadmap_bp
from blueprints.admin import admin_bp
from blueprints.assinatura import assinatura_bp, webhook as mp_webhook_view
from blueprints.notifications import notifications_bp
from blueprints.blog import blog_bp
from blueprints.guia import guia_bp
from blueprints.mail_web import mail_web_bp
from blueprints.whatsapp_admin import whatsapp_admin_bp
from blueprints.agenda import agenda_bp
from blueprints.convites import convites_bp
from blueprints.music_api import music_api_bp
from blueprints.realtime import realtime_bp
from blueprints.studios import studios_bp
from agenda_util import event_relative_label, format_event_datetime
from db import init_db
from extensions import init_scheduler
from util import highlight_chords_html, normalize_tom_label, format_date_short
from whatsapp_service import format_whatsapp_display
from flask_wtf.csrf import CSRFProtect, CSRFError
import os
from urllib.parse import urlparse
from flask_mail import Mail
import email_config

app = Flask(__name__)
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config.get(env, config['default']))
app.config.from_object('email_config')

# Cookie Secure: só HTTP local em development explícito
if env == 'development':
    app.config['SESSION_COOKIE_SECURE'] = False
elif os.getenv('ALLOW_HTTP_SESSION', '').lower() in ('1', 'true', 'yes'):
    app.logger.warning('ALLOW_HTTP_SESSION ignorado em produção — SESSION_COOKIE_SECURE permanece ativo')

canonical = (os.getenv('SETSYNC_CANONICAL_URL') or '').strip()
if canonical:
    parsed = urlparse(canonical)
    if parsed.scheme:
        app.config['PREFERRED_URL_SCHEME'] = parsed.scheme

mail = Mail(app)
csrf = CSRFProtect(app)


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    """Token CSRF inválido/expirado (ex.: logout em outra aba, botão voltar,
    formulário aberto há muito tempo). Em vez de um 400 cru, volta à página de
    origem — o novo GET emite um token válido e a nova tentativa funciona."""
    flash('Sua sessão expirou. Atualizamos a página, tente novamente.', 'warning')
    ref = request.referrer
    if ref:
        ref_host = urlparse(ref).netloc
        if not ref_host or ref_host == urlparse(request.host_url).netloc:
            return redirect(ref)
    return redirect(url_for('auth.login'))


@app.teardown_appcontext
def _release_db_connections(exc):
    """Fecha conexões de banco que vazaram na requisição (evita esgotar o Postgres)."""
    from database import close_leaked_connections
    leaked = close_leaked_connections()
    if leaked:
        app.logger.warning(
            'Fechadas %d conexão(ões) de banco não encerradas em %s %s',
            leaked, request.method if request else '?', request.path if request else '?',
        )


def _wants_json_response() -> bool:
    """True quando o cliente é AJAX/JSON (saves do front-end usam fetch com JSON)."""
    return (
        request.is_json
        or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        or request.accept_mimetypes.best == 'application/json'
        or request.path.startswith('/api')
    )


@app.errorhandler(Exception)
def handle_unexpected_error(e):
    """Erros não tratados: loga o traceback e responde de forma útil.

    Antes, uma exceção virava a página padrão 'Internal Server Error' do Flask
    (e os saves AJAX falhavam em silêncio). Agora o erro fica no log e o
    front-end recebe um JSON tratável.
    """
    if isinstance(e, HTTPException):
        return e  # 404/403/400/CSRF etc. seguem seu próprio tratamento
    if app.debug:
        raise e  # em desenvolvimento, mantém o debugger interativo
    app.logger.exception(
        'Erro não tratado em %s %s', request.method, request.path,
    )
    if _wants_json_response():
        return jsonify({'ok': False, 'error': 'Erro ao processar. Tente novamente.'}), 500
    try:
        err_path = os.path.join(app.root_path, 'templates', 'errors', '500.html')
        with open(err_path, encoding='utf-8') as f:
            return f.read(), 500
    except OSError:
        pass
    html = (
        '<!doctype html><html lang="pt-br"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Erro — SetSync</title>'
        '<style>body{font-family:system-ui,sans-serif;background:#0c0a09;color:#e7e5e4;'
        'display:flex;min-height:100vh;align-items:center;justify-content:center;margin:0;padding:1.5rem}'
        '.box{max-width:420px;text-align:center}h1{font-size:1.3rem;margin:0 0 .5rem}'
        'p{color:#a8a29e;font-size:.95rem;margin:0 0 1.25rem}'
        'a{display:inline-block;padding:10px 22px;background:#ea580c;color:#fff;'
        'text-decoration:none;border-radius:8px;font-weight:600}</style></head>'
        '<body><div class="box"><h1>Algo deu errado</h1>'
        '<p>Tivemos um problema ao processar sua solicitação. Tente novamente em instantes.</p>'
        '<a href="/">Voltar ao início</a></div></body></html>'
    )
    return html, 500

if env == 'production':
    from werkzeug.middleware.proxy_fix import ProxyFix
    if os.getenv('TRUST_PROXY', '1').lower() not in ('0', 'false', 'no'):
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

app.jinja_env.filters['highlight_chords'] = highlight_chords_html
app.jinja_env.filters['normalize_tom'] = normalize_tom_label
app.jinja_env.filters['date_short'] = format_date_short
app.jinja_env.filters['format_event_datetime'] = format_event_datetime
app.jinja_env.filters['event_relative_label'] = event_relative_label
app.jinja_env.filters['whatsapp_display'] = format_whatsapp_display


def _faq_to_schema(item: dict) -> dict:
    return {
        '@type': 'Question',
        'name': item['q'],
        'acceptedAnswer': {'@type': 'Answer', 'text': item['a']},
    }


app.jinja_env.filters['faq_to_schema'] = _faq_to_schema

with app.app_context():
    init_db()

_PWA_ASSET_PATHS = frozenset(('/sw.js', '/manifest.webmanifest'))
_SEO_ASSET_PATHS = frozenset(('/robots.txt', '/sitemap.xml', '/google47ebf77ba640d99c.html'))


@app.before_request
def before_request():
    if request.path in _PWA_ASSET_PATHS or request.path in _SEO_ASSET_PATHS:
        return
    from security import validate_request_host
    host_redirect = validate_request_host()
    if host_redirect is not None:
        return host_redirect
    if 'user_id' in session:
        session.permanent = True
        from db import is_superadmin as _is_superadmin
        session['is_superadmin'] = bool(_is_superadmin(session['user_id']))


@app.after_request
def security_headers(response):
    if request.path in _PWA_ASSET_PATHS:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers.pop('Set-Cookie', None)
        return response
    response.headers.setdefault('X-Frame-Options', 'DENY')
    response.headers.setdefault('X-Content-Type-Options', 'nosniff')
    response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
    response.headers.setdefault('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
    if env == 'production':
        response.headers.setdefault(
            'Strict-Transport-Security',
            'max-age=31536000; includeSubDomains',
        )
    if 'user_id' in session and request.method == 'GET':
        response.headers['Cache-Control'] = 'no-store, private'
    return response

# Registro de Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(legal_bp)
app.register_blueprint(bands_bp)
app.register_blueprint(cifras_import_bp)
app.register_blueprint(cifras_bp)
app.register_blueprint(setlists_bp)
app.register_blueprint(ajuda_bp)
app.register_blueprint(roadmap_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(assinatura_bp)
app.register_blueprint(notifications_bp)
app.register_blueprint(blog_bp)
app.register_blueprint(guia_bp)
app.register_blueprint(mail_web_bp)
app.register_blueprint(whatsapp_admin_bp)
app.register_blueprint(agenda_bp)
app.register_blueprint(convites_bp)
app.register_blueprint(music_api_bp)
app.register_blueprint(realtime_bp)
app.register_blueprint(studios_bp)
init_scheduler(app)

# Webhook Mercado Pago: POST externo sem CSRF de formulário
csrf.exempt(mp_webhook_view)

# API musical v1 — JSON/SVG para clientes externos
for _music_ep in (
    'music_api.catalog',
    'music_api.chords_index',
    'music_api.chords_detail',
    'music_api.scales_index',
    'music_api.arpeggios_index',
    'music_api.render_fretboard',
    'music_api.render_piano',
    'music_api.notation_vexflow',
    'music_api.telemetry_ndjson',
):
    _mv = app.view_functions.get(_music_ep)
    if _mv:
        csrf.exempt(_mv)

# APIs JSON autenticadas (login_required) — fetch do editor Chord Sheet / LeadSheet
for _csrf_json_endpoint in (
    'cifras.chordsheet_api_render',
    'cifras.chordsheet_api_transpose',
    'cifras.chordsheet_api_save',
    'cifras.leadsheet_api_gerar',
    'cifras.leadsheet_api_salvar',
    'cifras.leadsheet_api_analisar',
    'studios.api_room_slots',
    'ajuda.chat',
    'ajuda.nps_submit',
    'legal.cookie_consent',
):
    _view = app.view_functions.get(_csrf_json_endpoint)
    if _view:
        csrf.exempt(_view)


@app.errorhandler(404)
def page_not_found(e):
    if _wants_json_response():
        return jsonify({'ok': False, 'error': 'Não encontrado'}), 404
    return render_template('errors/404.html'), 404


@app.route('/login')
def login_redirect():
    """Atalho legado — /auth/login é a rota canônica."""
    return redirect(url_for('auth.login', **request.args))


@app.route('/health')
def health():
    return 'ok', 200


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    from monetizacao import planos_para_site, planos_estudio_para_site
    from db import count_bands, count_cifras, count_setlists, list_testimonials
    from cifras_tool.api_cifras_client import get_api_cifras_public_stats

    stats = {
        'bandas': count_bands(),
        'musicas': count_cifras(),
        'setlists': count_setlists(),
    }
    api_cifras_stats = get_api_cifras_public_stats()
    if api_cifras_stats.get('available'):
        stats['biblioteca'] = True

    return render_template(
        'home.html',
        planos_estudio=planos_estudio_para_site(),
        stats=stats,
        testimonials=list_testimonials(active_only=True),
    )


@app.route('/sw.js')
def service_worker():
    resp = make_response(send_from_directory(app.static_folder, 'sw.js'))
    resp.headers['Content-Type'] = 'application/javascript'
    resp.headers['Cache-Control'] = 'no-cache'
    resp.headers['Service-Worker-Allowed'] = '/'
    return resp


@app.route('/manifest.webmanifest')
def manifest():
    resp = make_response(send_from_directory(app.static_folder, 'manifest.webmanifest'))
    resp.headers['Content-Type'] = 'application/manifest+json; charset=utf-8'
    return resp


@app.route('/google47ebf77ba640d99c.html')
def google_site_verification():
    """Verificação de propriedade no Google Search Console."""
    resp = make_response(
        send_from_directory(app.root_path, 'google47ebf77ba640d99c.html')
    )
    resp.headers['Content-Type'] = 'text/html; charset=utf-8'
    return resp


@app.route('/robots.txt')
def robots_txt():
    """Orienta crawlers e aponta para o sitemap canônico."""
    from security import external_url_for

    sitemap_url = external_url_for('sitemap')
    body = (
        'User-agent: *\n'
        'Allow: /\n'
        '\n'
        'Disallow: /dashboard\n'
        'Disallow: /admin/\n'
        'Disallow: /bands/\n'
        'Disallow: /cifras/\n'
        'Disallow: /setlists/\n'
        'Disallow: /notifications/\n'
        'Disallow: /assinatura/\n'
        'Disallow: /setlist/\n'
        'Disallow: /letras/\n'
        'Disallow: /agenda/\n'
        '\n'
        f'Sitemap: {sitemap_url}\n'
    )
    resp = make_response(body)
    resp.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return resp


@app.route('/offline')
def offline():
    return render_template('offline.html')


@app.route('/setlist/<setlist_id>/exportar-pdf')
@login_required
def exportar_setlist_pdf(setlist_id):
    """Alias da rota de exportação PDF (especificação /setlist/...)."""
    from blueprints.setlists import exportar_pdf
    return exportar_pdf(setlist_id)



@app.route('/sitemap.xml')
def sitemap():
    from db import list_blog_posts
    from security import external_url_for

    from seo_pages import list_comparison_pages, list_seo_pages

    pages = [
        {'loc': external_url_for('index'), 'changefreq': 'weekly', 'priority': '1.0'},
        {'loc': external_url_for('assinatura_bp.bandas'), 'changefreq': 'monthly', 'priority': '0.9'},
        {'loc': external_url_for('guia.guia_index'), 'changefreq': 'weekly', 'priority': '0.92'},
        {'loc': external_url_for('assinatura_bp.igrejas'), 'changefreq': 'monthly', 'priority': '0.85'},
        {'loc': external_url_for('studios.landing'), 'changefreq': 'monthly', 'priority': '0.85'},
        {'loc': external_url_for('comece'), 'changefreq': 'monthly', 'priority': '0.88'},
        {'loc': external_url_for('blog.blog_index'), 'changefreq': 'daily', 'priority': '0.9'},
        {'loc': external_url_for('ajuda.index'), 'changefreq': 'monthly', 'priority': '0.75'},
        {'loc': external_url_for('auth.register'), 'changefreq': 'monthly', 'priority': '0.8'},
        {'loc': external_url_for('auth.login'), 'changefreq': 'yearly', 'priority': '0.4'},
    ]
    for page in list_comparison_pages():
        pages.append({
            'loc': external_url_for('guia.comparativo', slug=page['slug']),
            'changefreq': 'monthly',
            'priority': '0.78',
        })
    for page in list_seo_pages():
        if page.get('noindex'):
            continue
        pages.append({
            'loc': external_url_for('guia.guia_page', slug=page['slug']),
            'changefreq': 'monthly',
            'priority': '0.72' if page.get('premium') else '0.65',
        })
    for post in list_blog_posts(published_only=True):
        from util import format_date_short
        lastmod = format_date_short(post.get('atualizado_em') or post.get('publicado_em'))
        pages.append({
            'loc': external_url_for('blog.blog_post', slug=post['slug']),
            'changefreq': 'monthly',
            'priority': '0.7',
            'lastmod': lastmod,
        })
    xml = render_template('sitemap.xml', pages=pages)
    resp = make_response(xml)
    resp.headers['Content-Type'] = 'application/xml; charset=utf-8'
    resp.headers['Cache-Control'] = 'public, max-age=3600'
    return resp


@app.route('/comece')
def comece():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    plano = (request.args.get('plano') or '').strip().lower()
    if plano in ('worship', 'pro', 'individual'):
        session['register_plano_intent'] = plano
        session.modified = True
    return render_template('comece.html', plano_intent=plano or None)


@app.route('/dashboard/onboarding/dismiss', methods=['POST'])
@login_required
def dismiss_onboarding_checklist():
    from db import dismiss_onboarding_checklist as _dismiss

    _dismiss(session['user_id'])
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
@login_required
def dashboard():
    from db import (
        get_user_bands, get_owned_bands, get_all_bands,
        enrich_bands_for_display, is_superadmin,
    )
    from monetizacao import enrich_bands_plano, resumo_planos_usuario, dias_restantes_trial, get_assinatura_banda

    from onboarding import get_onboarding_progress
    from band_member_invites import list_pending_invites_for_user
    from cifras_tool.api_cifras_client import get_api_cifras_public_stats

    api_cifras_stats = get_api_cifras_public_stats()

    user_id = session['user_id']
    onboarding = get_onboarding_progress(user_id)
    pending_band_invites = list_pending_invites_for_user(user_id)
    sa = is_superadmin(user_id)

    def _trial_ctx(bands_list):
        for b in bands_list:
            dias = dias_restantes_trial(b['id'])
            if dias is not None:
                return {'ativo': True, 'dias': dias, 'band_name': b['name']}
            ass = get_assinatura_banda(b['id'])
            if ass.trial_usado and not ass.trial_ativo():
                return {'expirado': True, 'band_name': b['name']}
        return None

    from models_agenda import (
        get_events_scale_summaries,
        get_events_where_user_assigned,
        get_upcoming_events_for_user,
    )
    from models_band_team import (
        list_events_pending_responses_for_editor,
        list_pending_assignments_for_user,
    )
    from models_studio import (
        enrich_studios_for_admin,
        enrich_studios_for_dashboard,
        list_all_studios,
        studio_primary_home_endpoint,
    )

    if not sa:
        studio_home = studio_primary_home_endpoint(user_id)
        if studio_home:
            ep, kwargs = studio_home
            return redirect(url_for(ep, **kwargs))

    pending_scale = list_pending_assignments_for_user(user_id)
    pending_scale_admin = list_events_pending_responses_for_editor(user_id)
    my_studios = enrich_studios_for_dashboard(user_id) if not sa else []

    def _enrich_upcoming(events):
        ids = [e['id'] for e in events]
        scaled = get_events_where_user_assigned(user_id, ids)
        summaries = get_events_scale_summaries(ids)
        for e in events:
            e['user_scaled'] = e['id'] in scaled
            s = summaries.get(e['id'], {})
            e['scale_preview'] = s.get('preview', '')
        return events

    def _growth_ctx(owned):
        if sa:
            return {}
        from db import user_should_see_nps, user_should_see_pwa_prompt
        from growth_upsell import get_dashboard_upsells, show_referral_card
        return {
            'upsell_alerts': get_dashboard_upsells(user_id, owned_bands=owned),
            'show_referral_card': show_referral_card(user_id),
            'show_nps_modal': user_should_see_nps(user_id),
            'show_pwa_prompt': user_should_see_pwa_prompt(user_id),
        }

    if sa:
        all_bands = enrich_bands_plano(enrich_bands_for_display(get_all_bands()))
        owned_bands = enrich_bands_plano(enrich_bands_for_display(get_owned_bands(user_id)))
        all_studios = enrich_studios_for_admin(list_all_studios())
        upcoming_events = _enrich_upcoming(
            get_upcoming_events_for_user(user_id, all_bands=True, limit=8),
        )
        return render_template(
            'dashboard.html',
            bands=all_bands,
            owned_bands=owned_bands,
            all_studios=all_studios,
            upcoming_events=upcoming_events,
            is_superadmin=True,
            planos_resumo=resumo_planos_usuario(owned_bands),
            trial_ui=_trial_ctx(owned_bands),
            onboarding=onboarding,
            pending_band_invites=pending_band_invites,
            pending_scale=pending_scale,
            pending_scale_admin=pending_scale_admin,
            api_cifras_stats=api_cifras_stats,
            my_studios=[],
        )
    owned_bands = enrich_bands_plano(enrich_bands_for_display(get_owned_bands(user_id)))
    bands = enrich_bands_plano(enrich_bands_for_display(get_user_bands(user_id)))
    upcoming_events = _enrich_upcoming(get_upcoming_events_for_user(user_id, limit=8))
    growth = _growth_ctx(owned_bands)
    return render_template(
        'dashboard.html',
        bands=bands,
        owned_bands=owned_bands,
        upcoming_events=upcoming_events,
        is_superadmin=False,
        planos_resumo=resumo_planos_usuario(owned_bands),
        trial_ui=_trial_ctx(owned_bands),
        onboarding=onboarding,
        pending_band_invites=pending_band_invites,
        pending_scale=pending_scale,
        pending_scale_admin=pending_scale_admin,
        api_cifras_stats=api_cifras_stats,
        my_studios=my_studios,
        **growth,
    )


_SEO_PUBLIC_ENDPOINTS = frozenset({
    'index',
    'assinatura_bp.bandas',
    'guia.guia_index',
    'guia.guia_page',
    'comece',
    'guia.comparativo',
    'blog.blog_index',
    'blog.blog_post',
    'ajuda.index',
    'assinatura_bp.igrejas',
    'studios.landing',
    'studios.booking_landing',
    'auth.register',
    'auth.login',
    'legal.privacidade',
    'legal.termos',
    'sitemap',
    'robots_txt',
    'google_site_verification',
})


@app.context_processor
def inject_google_ads():
    from flask import request as _req
    from google_ads import (
        consume_funnel_events,
        get_google_ads_config,
        get_google_analytics_id,
        google_ads_ativo,
        google_analytics_ativo,
    )
    from lgpd import may_load_tracking

    ativo = google_ads_ativo()
    funnel_events: list[str] = []
    _fire = frozenset({
        'auth.cadastro_concluido',
        'dashboard',
        'bands.view',
        'cifras.view',
    })
    if ativo and may_load_tracking() and _req.endpoint in _fire:
        funnel_events = consume_funnel_events()

    return dict(
        google_ads=get_google_ads_config(),
        google_ads_ativo=ativo,
        google_analytics_id=get_google_analytics_id(),
        google_analytics_ativo=google_analytics_ativo(),
        google_ads_fire_signup='signup' in funnel_events,
        google_ads_funnel_events=funnel_events,
        google_ads_enhanced_data={},
    )


@app.context_processor
def inject_site_config():
    from config import whatsapp_number, whatsapp_message
    from mercadopago_trust import show_mercadopago_trust
    from db import is_superadmin as _is_superadmin
    from config import google_oauth_enabled
    from security import external_url_for as _external_url_for
    from flask import request as _request

    mail_inbox_url = None
    user_id = session.get('user_id')
    if user_id and _is_superadmin(user_id):
        try:
            mail_inbox_url = url_for('mail_web.inbox')
        except RuntimeError:
            mail_inbox_url = '/admin/email/'

    from seo_pages import faq_entries as _faq_entries

    ep = _request.endpoint if _request else None
    site_url = _external_url_for('index')
    return dict(
        faq_entries=_faq_entries(),
        whatsapp_number=whatsapp_number(),
        whatsapp_message=whatsapp_message(),
        webmail_url=mail_inbox_url,
        mail_inbox_url=mail_inbox_url,
        external_url_for=_external_url_for,
        site_url=site_url,
        site_og_image=_external_url_for('static', filename='logoSetSync.png'),
        google_oauth_enabled=google_oauth_enabled(),
        show_mercadopago_trust=show_mercadopago_trust(),
        seo_noindex=bool(ep and ep not in _SEO_PUBLIC_ENDPOINTS),
    )


@app.context_processor
def inject_user():
    user_id = session.get('user_id')
    username = session.get('username')
    display_name = (session.get('display_name') or '').strip()
    try:
        cifras_import_tool_url = url_for('cifras_import.embed_tool')
    except RuntimeError:
        cifras_import_tool_url = '/cifras/import/tool'
    from db import is_superadmin as _is_superadmin, count_unread_notifications, user_display_name
    from band_member_invites import inviter_display_name as _inviter_display_name
    from blueprints.cifras import cifra_display_key
    from models_studio import is_studio_primary_user, studio_primary_home_endpoint
    unread = count_unread_notifications(user_id) if user_id else 0
    is_studio_primary = bool(user_id and is_studio_primary_user(user_id))
    nav_home_url = url_for('dashboard')
    if user_id:
        studio_home = studio_primary_home_endpoint(user_id)
        if studio_home:
            ep, kwargs = studio_home
            nav_home_url = url_for(ep, **kwargs)
    return dict(
        cifra_display_key=cifra_display_key,
        user_display_name=user_display_name,
        inviter_display_name=_inviter_display_name,
        notifications_unread=unread,
        is_studio_primary=is_studio_primary,
        nav_home_url=nav_home_url,
        current_user={
            'id': user_id, 'username': username, 'display_name': display_name,
            'name': display_name or username, 'is_authenticated': user_id is not None,
            'is_superadmin': bool(user_id and _is_superadmin(user_id)),
        },
        cifras_import_tool_url=cifras_import_tool_url,
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=os.getenv('FLASK_ENV') == 'development')
