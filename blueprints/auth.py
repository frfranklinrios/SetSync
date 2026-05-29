import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from db import (create_user, get_user_by_username, get_user, verify_password,
                get_user_by_google_id, create_google_user, get_user_by_email,
                update_user_display_name, is_superadmin)
from google_oauth import handle_google_callback, get_authorization_url
import functools
from itsdangerous import URLSafeTimedSerializer
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def _is_safe_redirect(target):
    """Evita open redirect: aceita apenas paths relativos do mesmo host."""
    if not target or not target.startswith('/'):
        return False
    return not target.startswith('//')


def send_reset_email(email, token):
    from flask_mail import Message
    mail = current_app.extensions['mail']
    link = url_for('auth.reset_senha', token=token, _external=True)
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
            s = URLSafeTimedSerializer(os.environ.get('SECRET_KEY', 'dev'))
            token = s.dumps(email, salt='recuperar-senha')
            send_reset_email(email, token)
        message = 'Se o e-mail estiver cadastrado, um link de recuperação foi enviado.'
        return render_template('recuperar_senha.html', message=message)
    return render_template('recuperar_senha.html')

@auth_bp.route('/reset/<token>', methods=['GET', 'POST'])
def reset_senha(token):
    from werkzeug.security import generate_password_hash
    message = None
    s = URLSafeTimedSerializer(os.environ.get('SECRET_KEY', 'dev'))
    try:
        email = s.loads(token, salt='recuperar-senha', max_age=3600)
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
        elif len(password) < 6:
            message = 'A senha deve ter no mínimo 6 caracteres.'
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
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        display_name = request.form.get('display_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        
        if not username or not display_name or not email or not password:
            flash('Preencha todos os campos', 'danger')
            return render_template('register.html')

        if len(display_name) < 2:
            flash('Nome deve ter no mínimo 2 caracteres', 'danger')
            return render_template('register.html')
        if len(display_name) > 60:
            flash('Nome deve ter no máximo 60 caracteres', 'danger')
            return render_template('register.html')
        
        if password != confirm:
            flash('Senhas não conferem', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Senha deve ter no mínimo 6 caracteres', 'danger')
            return render_template('register.html')
        
        if get_user_by_username(username):
            flash('Usuário já existe', 'danger')
            return render_template('register.html')
        
        user_id = create_user(username, email, password, display_name=display_name)
        
        if not user_id:
            flash('Email já cadastrado', 'danger')
            return render_template('register.html')
        
        flash('Conta criada com sucesso! Faça login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = get_user_by_username(username)
        
        if user and verify_password(user['id'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['display_name'] = (user.get('display_name') or '').strip()
            session['is_superadmin'] = is_superadmin(user['id'])
            session.permanent = True
            
            next_page = request.args.get('next')
            if next_page and _is_safe_redirect(next_page):
                return redirect(next_page)
            if not session['display_name']:
                return redirect(url_for('auth.definir_nome', next=next_page or url_for('dashboard')))
            return redirect(url_for('dashboard'))
        
        flash('Usuário ou senha incorretos', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Você saiu da conta', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/google')
def google():
    return redirect(get_authorization_url())

@auth_bp.route('/google/callback')
def google_callback():
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
            # Atualizar usuário existente com Google ID
            db = __import__('db').get_db()
            c = db.cursor()
            c.execute('UPDATE users SET google_id = ? WHERE id = ?',
                      (userinfo['id'], existing_user['id']))
            db.commit()
            db.close()
            user = existing_user
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
    
    # Login do usuário
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['display_name'] = (user.get('display_name') or '').strip()
    session['is_superadmin'] = is_superadmin(user['id'])
    session.permanent = True
    
    if not session['display_name']:
        return redirect(url_for('auth.definir_nome', next=url_for('dashboard')))

    flash(f'Bem-vindo, {session.get("display_name") or user["username"]}!', 'success')
    return redirect(url_for('dashboard'))


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

