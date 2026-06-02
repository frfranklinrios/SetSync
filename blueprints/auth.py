import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from db import (create_user, get_user_by_username, get_user_by_login, get_user, verify_password,
                get_user_by_google_id, create_google_user, get_user_by_email,
                update_user_display_name, is_superadmin, get_band)
from band_invites import parse_band_invite_token, apply_band_invite
import band_notifications as bn
from google_oauth import handle_google_callback, get_authorization_url
import functools
from itsdangerous import URLSafeTimedSerializer
from security import (
    check_rate_limit, clear_rate_limit, external_url_for, make_oauth_state,
    safe_redirect_path, verify_oauth_state,
)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
MIN_PASSWORD_LEN = 10


def _password_reset_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt='recuperar-senha')


def _is_safe_redirect(target):
    """Evita open redirect: aceita apenas paths relativos do mesmo host."""
    if not target or not target.startswith('/'):
        return False
    return not target.startswith('//')


def _invite_token_from_request():
    return (
        request.form.get('convite_token', '').strip()
        or request.args.get('convite', '').strip()
    )


def _login_user_session(user):
    session.clear()
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['display_name'] = (user.get('display_name') or '').strip()
    session['is_superadmin'] = is_superadmin(user['id'])
    session.permanent = True


def _redirect_after_auth(user, invite_token: str | None = None):
    """Redireciona após login/cadastro; aplica convite de banda se houver."""
    band_id = parse_band_invite_token(invite_token)
    if band_id:
        result = apply_band_invite(user['id'], band_id)
        if result:
            band = get_band(band_id)
            name = band['name'] if band else 'banda'
            if result == 'added':
                bn.member_joined_via_invite(band_id, user['id'])
                flash(f'Você entrou na banda {name}!', 'success')
            if not session.get('display_name'):
                return redirect(url_for('auth.definir_nome', next=url_for('bands.view', band_id=band_id)))
            return redirect(url_for('bands.view', band_id=band_id))

    next_page = request.args.get('next')
    if next_page and safe_redirect_path(next_page):
        return redirect(next_page)
    if not session.get('display_name'):
        return redirect(url_for('auth.definir_nome', next=url_for('dashboard')))
    return redirect(url_for('dashboard'))


def send_reset_email(email, token):
    from flask_mail import Message
    mail = current_app.extensions['mail']
    link = external_url_for('auth.reset_senha', token=token)
    msg = Message('Recuperação de senha - SetSync', recipients=[email])
    msg.body = f'Para redefinir sua senha, clique no link: {link}\nSe você não solicitou, ignore este e-mail.'
    mail.send(msg)

@auth_bp.route('/recuperar-senha', methods=['GET', 'POST'])
def recuperar_senha():
    message = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        user = get_user_by_email(email)
        if user:
            token = _password_reset_serializer().dumps(email)
            send_reset_email(email, token)
        message = 'Se o e-mail estiver cadastrado, um link de recuperação foi enviado.'
        return render_template('recuperar_senha.html', message=message)
    return render_template('recuperar_senha.html')

@auth_bp.route('/reset/<token>', methods=['GET', 'POST'])
def reset_senha(token):
    from werkzeug.security import generate_password_hash
    message = None
    s = _password_reset_serializer()
    try:
        email = s.loads(token, max_age=3600)
    except Exception:
        message = 'Link inválido ou expirado.'
        return render_template('reset_senha.html', message=message)
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        if not password or not confirm:
            message = 'Preencha todos os campos.'
        elif password != confirm:
            message = 'As senhas não conferem.'
        elif len(password) < MIN_PASSWORD_LEN:
            message = f'A senha deve ter no mínimo {MIN_PASSWORD_LEN} caracteres.'
        else:
            db = __import__('db').get_db()
            c = db.cursor()
            c.execute('UPDATE users SET password_hash = ? WHERE email = ?', (generate_password_hash(password), email))
            db.commit()
            db.close()
            message = 'Senha redefinida com sucesso!'
            return render_template('reset_senha.html', message=message)
    return render_template('reset_senha.html', message=message)

def login_required(f):
    """Decorator para rotas que requerem login"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            nxt = safe_redirect_path(request.path)
            if nxt:
                return redirect(url_for('auth.login', next=nxt))
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/convite/<token>')
def convite(token):
    """Entrada via link de convite: cadastro, login ou entra direto se já logado."""
    band_id = parse_band_invite_token(token)
    band = get_band(band_id) if band_id else None
    if not band:
        flash('Convite inválido ou expirado.', 'danger')
        return redirect(url_for('auth.login'))

    if 'user_id' in session:
        result = apply_band_invite(session['user_id'], band_id)
        if result == 'added':
            bn.member_joined_via_invite(band_id, session['user_id'])
            flash(f'Você entrou na banda {band["name"]}!', 'success')
        elif result == 'already':
            flash(f'Você já faz parte da banda {band["name"]}.', 'info')
        return redirect(url_for('bands.view', band_id=band_id))

    return redirect(url_for('auth.register', convite=token))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    invite_token = _invite_token_from_request()
    band_id = parse_band_invite_token(invite_token)
    invite_band = get_band(band_id) if band_id else None

    if 'user_id' in session:
        if band_id and apply_band_invite(session['user_id'], band_id):
            return redirect(url_for('bands.view', band_id=band_id))
        return redirect(url_for('dashboard'))

    def _register_ctx():
        return dict(invite_token=invite_token, invite_band=invite_band)

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        display_name = request.form.get('display_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        
        if not username or not display_name or not email or not password:
            flash('Preencha todos os campos', 'danger')
            return render_template('register.html', **_register_ctx())

        if len(display_name) < 2:
            flash('Nome deve ter no mínimo 2 caracteres', 'danger')
            return render_template('register.html', **_register_ctx())
        if len(display_name) > 60:
            flash('Nome deve ter no máximo 60 caracteres', 'danger')
            return render_template('register.html', **_register_ctx())
        
        if password != confirm:
            flash('Senhas não conferem', 'danger')
            return render_template('register.html', **_register_ctx())
        
        if len(password) < MIN_PASSWORD_LEN:
            flash(f'Senha deve ter no mínimo {MIN_PASSWORD_LEN} caracteres', 'danger')
            return render_template('register.html', **_register_ctx())
        
        if get_user_by_username(username):
            flash('Usuário já existe', 'danger')
            return render_template('register.html', **_register_ctx())
        
        user_id = create_user(username, email, password, display_name=display_name)
        
        if not user_id:
            flash('Email já cadastrado', 'danger')
            return render_template(
                'register.html',
                invite_token=invite_token,
                invite_band=invite_band,
            )

        user = get_user(user_id)
        _login_user_session(user)
        if invite_band:
            flash(f'Conta criada! Você já está na banda {invite_band["name"]}.', 'success')
        else:
            flash('Conta criada com sucesso!', 'success')
        return _redirect_after_auth(user, invite_token)

    return render_template(
        'register.html',
        invite_token=invite_token,
        invite_band=invite_band,
    )

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    invite_token_early = _invite_token_from_request()
    band_id_early = parse_band_invite_token(invite_token_early)
    if 'user_id' in session:
        if band_id_early and apply_band_invite(session['user_id'], band_id_early):
            return redirect(url_for('bands.view', band_id=band_id_early))
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        login_id = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        rate_key = f'login:{request.remote_addr}:{login_id.lower()}'
        if not check_rate_limit(rate_key):
            flash('Muitas tentativas. Aguarde alguns minutos e tente novamente.', 'danger')
            return render_template(
                'login.html',
                invite_token=_invite_token_from_request(),
                invite_band=get_band(parse_band_invite_token(_invite_token_from_request())) if _invite_token_from_request() else None,
            )

        user = get_user_by_login(login_id)

        if user and verify_password(user['id'], password):
            clear_rate_limit(rate_key)
            _login_user_session(user)
            invite_token = _invite_token_from_request()
            return _redirect_after_auth(user, invite_token)

        flash('Usuário ou senha incorretos', 'danger')

    invite_token = _invite_token_from_request()
    invite_band = get_band(parse_band_invite_token(invite_token)) if invite_token else None
    return render_template(
        'login.html',
        invite_token=invite_token,
        invite_band=invite_band,
    )

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('Você saiu da conta', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/google')
def google():
    token = request.args.get('convite', '').strip()
    if token and parse_band_invite_token(token):
        session['pending_band_invite'] = token
        session.modified = True
    state = make_oauth_state()
    session['oauth_state'] = state
    session.modified = True
    return redirect(get_authorization_url(state))

@auth_bp.route('/google/callback')
def google_callback():
    if not verify_oauth_state(request.args.get('state')):
        flash('Sessão OAuth inválida ou expirada. Tente novamente.', 'danger')
        return redirect(url_for('auth.login'))

    code = request.args.get('code')
    
    if not code:
        flash('Erro na autenticação com Google', 'danger')
        return redirect(url_for('auth.login'))
    
    userinfo = handle_google_callback(code)
    
    if not userinfo:
        flash('Erro ao obter informações do Google', 'danger')
        return redirect(url_for('auth.login'))
    
    # Verificar se usuário já existe
    user = get_user_by_google_id(userinfo['id'])
    
    if not user:
        # Verificar se email já está cadastrado (migração de usuário normal)
        existing_user = get_user_by_email(userinfo['email'])
        
        if existing_user:
            flash(
                'Já existe uma conta com este e-mail. Entre com sua senha para continuar.',
                'warning',
            )
            return redirect(url_for('auth.login'))
        else:
            # Criar novo usuário
            user_id = create_google_user(
                userinfo['id'],
                userinfo['email'],
                userinfo['username'],
                display_name=(userinfo.get('name') or '').strip() or None,
            )
            if not user_id:
                flash('Erro ao criar conta', 'danger')
                return redirect(url_for('auth.login'))
            user = get_user(user_id)
    
    _login_user_session(user)
    flash(f'Bem-vindo, {session.get("display_name") or user["username"]}!', 'success')
    pending = session.pop('pending_band_invite', None)
    return _redirect_after_auth(user, pending)


@auth_bp.route('/nome', methods=['GET', 'POST'])
@login_required
def definir_nome():
    """Pede o nome de exibição para contas antigas sem display_name."""
    next_page = request.args.get('next') or url_for('dashboard')
    if not _is_safe_redirect(next_page):
        next_page = url_for('dashboard')

    if request.method == 'POST':
        nome = (request.form.get('display_name') or '').strip()
        if len(nome) < 2:
            flash('Digite um nome com pelo menos 2 caracteres.', 'warning')
            return render_template('definir_nome.html', next=next_page, suggested=session.get('username') or '')
        if len(nome) > 60:
            flash('Digite um nome com no máximo 60 caracteres.', 'warning')
            return render_template('definir_nome.html', next=next_page, suggested=session.get('username') or '')

        update_user_display_name(session['user_id'], nome)
        session['display_name'] = nome
        flash(f'Perfeito, {nome}!', 'success')
        return redirect(next_page)

    if session.get('display_name'):
        return redirect(next_page)
    return render_template('definir_nome.html', next=next_page, suggested=session.get('username') or '')

