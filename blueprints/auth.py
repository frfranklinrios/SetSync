from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import (create_user, get_user_by_username, get_user, verify_password,
                get_user_by_google_id, create_google_user, get_user_by_email)
from google_oauth import handle_google_callback, get_authorization_url
import functools

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

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
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        
        if not username or not email or not password:
            flash('Preencha todos os campos', 'danger')
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
        
        user_id = create_user(username, email, password)
        
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
            session.permanent = request.form.get('remember') is not None
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        
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
            user_id = create_google_user(userinfo['id'], userinfo['email'], userinfo['username'])
            if not user_id:
                flash('Erro ao criar conta', 'danger')
                return redirect(url_for('auth.login'))
            user = get_user(user_id)
    
    # Login do usuário
    session['user_id'] = user['id']
    session['username'] = user['username']
    session.permanent = True
    
    flash(f'Bem-vindo, {user["username"]}!', 'success')
    return redirect(url_for('dashboard'))

