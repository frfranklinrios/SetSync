
from flask import Flask, render_template, redirect, url_for, session, send_from_directory, make_response, request
from config import config
from blueprints.auth import auth_bp, login_required
from blueprints.bands import bands_bp
from blueprints.cifras import cifras_bp
from blueprints.setlists import setlists_bp
from blueprints.cifras_import import cifras_import_bp
from blueprints.ajuda import ajuda_bp
from db import init_db
from util import highlight_chords_html
import os
from flask_mail import Mail
import email_config


app = Flask(__name__)
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config.get(env, config['default']))
app.config.from_object('email_config')
mail = Mail(app)

# Filtro Jinja2 para destaque de acordes
app.jinja_env.filters['highlight_chords'] = highlight_chords_html

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

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.login'))


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

@app.route('/dashboard')
@login_required
def dashboard():
    from db import get_user_bands, get_owned_bands, get_band_members, get_band_cifras, get_user
    user_id = session['user_id']

    def enrich(bands):
        result = []
        for band in bands:
            band = dict(band)
            band['members'] = get_band_members(band['id'])
            band['cifras'] = get_band_cifras(band['id'])
            owner = get_user(band['owner_id'])
            band['owner'] = owner or {}
            result.append(band)
        return result

    bands = enrich(get_user_bands(user_id))
    owned_bands = enrich(get_owned_bands(user_id))
    return render_template('dashboard.html', bands=bands, owned_bands=owned_bands)

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

    return dict(
        current_user={
            'id': user_id,
            'username': username,
            'display_name': display_name,
            'name': display_name or username,
            'is_authenticated': user_id is not None,
        },
        cifras_import_tool_url=cifras_import_tool_url,
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
