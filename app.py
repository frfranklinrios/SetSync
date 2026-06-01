
from flask import Flask, render_template, redirect, url_for, session, send_from_directory, make_response, request
from config import config
from blueprints.auth import auth_bp, login_required
from blueprints.bands import bands_bp
from blueprints.cifras import cifras_bp
from blueprints.setlists import setlists_bp
from blueprints.cifras_import import cifras_import_bp
from blueprints.ajuda import ajuda_bp
from blueprints.admin import admin_bp
from blueprints.assinatura import assinatura_bp
from db import init_db
from extensions import init_scheduler
from util import highlight_chords_html, normalize_tom_label
import os
from flask_mail import Mail
import email_config


app = Flask(__name__)
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config.get(env, config['default']))
app.config.from_object('email_config')
# Login em http://127.0.0.1: com .env de produção (SESSION_COOKIE_SECURE=1) não persiste sessão
if env == 'development' or os.getenv('ALLOW_HTTP_SESSION', '').lower() in ('1', 'true', 'yes'):
    app.config['SESSION_COOKIE_SECURE'] = False
mail = Mail(app)

if env == 'production':
    from werkzeug.middleware.proxy_fix import ProxyFix

    if os.getenv('TRUST_PROXY', '1').lower() not in ('0', 'false', 'no'):
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    _sk = (os.getenv('SECRET_KEY') or '').strip()
    _weak = {
        '',
        'dev-key-change-in-production',
        'sua-chave-secreta-aqui-mude-em-producao',
    }
    if _sk in _weak:
        app.logger.warning(
            'SECRET_KEY ausente ou padrão — defina uma chave forte no .env antes do deploy.'
        )

# Filtro Jinja2 para destaque de acordes
app.jinja_env.filters['highlight_chords'] = highlight_chords_html
app.jinja_env.filters['normalize_tom'] = normalize_tom_label

# Inicializar banco de dados na criação da app
with app.app_context():
    init_db()

_PWA_ASSET_PATHS = frozenset(('/sw.js', '/manifest.webmanifest'))


@app.before_request
def before_request():
    # Não tocar na sessão em assets PWA — evita Vary: Cookie no service worker (Safari/iOS).
    if request.path in _PWA_ASSET_PATHS:
        return
    if 'user_id' in session:
        session.permanent = True


@app.after_request
def pwa_asset_headers(response):
    if request.path not in _PWA_ASSET_PATHS:
        return response
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers.pop('Set-Cookie', None)
    return response

# Registrar blueprints

app.register_blueprint(auth_bp)
app.register_blueprint(bands_bp)
app.register_blueprint(cifras_import_bp)
app.register_blueprint(cifras_bp)
app.register_blueprint(setlists_bp)
app.register_blueprint(ajuda_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(assinatura_bp)
init_scheduler(app)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    from monetizacao import planos_para_site

    return render_template('home.html', planos_site=planos_para_site())


# ── PWA ─────────────────────────────────────────────────────────
@app.route('/sw.js')
def service_worker():
    """Service worker must be served from root to claim full scope."""
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


@app.route('/offline')
def offline():
    return render_template('offline.html')


@app.route('/setlist/<setlist_id>/exportar-pdf')
@login_required
def exportar_setlist_pdf(setlist_id):
    """Alias da rota de exportação PDF (especificação /setlist/...)."""
    from blueprints.setlists import exportar_pdf
    return exportar_pdf(setlist_id)

@app.route('/dashboard')
@login_required
def dashboard():
    from db import (
        get_user_bands, get_owned_bands, get_all_bands,
        enrich_bands_for_display, is_superadmin,
    )
    from monetizacao import enrich_bands_plano, resumo_planos_usuario

    user_id = session['user_id']
    sa = is_superadmin(user_id)

    if sa:
        all_bands = enrich_bands_plano(enrich_bands_for_display(get_all_bands()))
        owned_bands = enrich_bands_plano(enrich_bands_for_display(get_owned_bands(user_id)))
        return render_template(
            'dashboard.html',
            bands=all_bands,
            owned_bands=owned_bands,
            is_superadmin=True,
            planos_resumo=resumo_planos_usuario(owned_bands),
        )

    bands = enrich_bands_plano(enrich_bands_for_display(get_user_bands(user_id)))
    owned_bands = enrich_bands_plano(enrich_bands_for_display(get_owned_bands(user_id)))
    return render_template(
        'dashboard.html',
        bands=bands,
        owned_bands=owned_bands,
        is_superadmin=False,
        planos_resumo=resumo_planos_usuario(owned_bands),
    )

@app.context_processor
def inject_user():
    """Disponibiliza informações do usuário e URL da ferramenta de cifras nos templates."""
    from flask import url_for

    user_id = session.get('user_id')
    username = session.get('username')
    display_name = (session.get('display_name') or '').strip()

    try:
        cifras_import_tool_url = url_for('cifras_import.embed_tool')
    except RuntimeError:
        cifras_import_tool_url = '/cifras/import/tool'

    from db import is_superadmin as _is_superadmin
    from blueprints.cifras import cifra_display_key

    return dict(
        cifra_display_key=cifra_display_key,
        current_user={
            'id': user_id,
            'username': username,
            'display_name': display_name,
            'name': display_name or username,
            'is_authenticated': user_id is not None,
            'is_superadmin': bool(user_id and _is_superadmin(user_id)),
        },
        cifras_import_tool_url=cifras_import_tool_url,
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
