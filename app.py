
from flask import Flask, render_template, redirect, url_for, session
from config import config
from blueprints.auth import auth_bp, login_required
from blueprints.bands import bands_bp
from blueprints.cifras import cifras_bp
from blueprints.setlists import setlists_bp
from db import init_db
from util import highlight_chords_html
import os
from flask_mail import Mail
import email_config


app = Flask(__name__)
app.config.from_object(config['development'])
app.config.from_object('email_config')
mail = Mail(app)

# Filtro Jinja2 para destaque de acordes
app.jinja_env.filters['highlight_chords'] = highlight_chords_html

# Inicializar banco de dados na criação da app
with app.app_context():
    init_db()

@app.before_request
def before_request():
    # Manter sessão permanente se necessário
    if 'user_id' in session:
        session.permanent = True

# Registrar blueprints

app.register_blueprint(auth_bp)
app.register_blueprint(bands_bp)
app.register_blueprint(cifras_bp)
app.register_blueprint(setlists_bp)

print('MAPEAMENTO DE ROTAS:')
print(app.url_map)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.login'))

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
    """Disponibiliza informações do usuário nos templates"""
    user_id = session.get('user_id')
    username = session.get('username')
    return dict(current_user={'id': user_id, 'username': username, 'is_authenticated': user_id is not None})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
