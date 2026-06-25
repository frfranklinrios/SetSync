import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from db import (create_user, get_user_by_username, get_user_by_login, get_user, verify_password,
                get_user_by_google_id, create_google_user, get_user_by_email,
                update_user_display_name, update_user_profile, update_user_password_by_email,
                is_superadmin, get_band, touch_user_last_login, user_has_phone)
from whatsapp_service import normalize_whatsapp_phone
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

# Rotas isentas de pedir nome ou WhatsApp (evita loop de redirect).
_SETUP_PROMPT_EXEMPT = frozenset({
    'auth.definir_nome',
    'auth.definir_whatsapp',
    'auth.perfil',
    'auth.logout',
    'auth.login',
    'auth.register',
    'auth.recuperar_senha',
    'auth.reset_senha',
    'auth.google',
    'auth.google_callback',
    'auth.convite',
    'auth.cadastro_concluido',
    'convites.index',
    'convites.aceitar',
    'convites.recusar',
})


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
    touch_user_last_login(user['id'])


def _auth_setup_redirect(next_page: str):
    """Nome → WhatsApp → destino (após login/cadastro)."""
    if not session.get('display_name'):
        return redirect(url_for('auth.definir_nome', next=next_page))
    if _should_prompt_phone():
        return redirect(url_for('auth.definir_whatsapp', next=next_page))
    return redirect(next_page)


def _should_prompt_display_name() -> bool:
    if (session.get('display_name') or '').strip():
        return False
    user = get_user(session.get('user_id'))
    if not user:
        return False
    nome = (user.get('display_name') or '').strip()
    if nome:
        session['display_name'] = nome
        session.modified = True
        return False
    return True


def _should_prompt_phone() -> bool:
    if session.get('skip_phone_prompt'):
        return False
    user = get_user(session.get('user_id'))
    return bool(user and not user_has_phone(user))


def _auth_destination_path(user, invite_token: str | None = None) -> str:
    """Destino final após login/cadastro (sem página de conversão)."""
    band_id = parse_band_invite_token(invite_token)
    if band_id:
        result = apply_band_invite(user['id'], band_id)
        if result:
            band = get_band(band_id)
            name = band['name'] if band else 'banda'
            if result == 'added':
                bn.member_joined_via_invite(band_id, user['id'])
                flash(f'Você entrou na banda {name}!', 'success')
            return url_for('bands.view', band_id=band_id)

    next_page = request.args.get('next')
    if next_page and safe_redirect_path(next_page):
        return next_page
    from models_studio import studio_primary_home_endpoint
    studio_home = studio_primary_home_endpoint(user['id'])
    if studio_home:
        ep, kwargs = studio_home
        return url_for(ep, **kwargs)
    return url_for('dashboard')


def _redirect_after_auth(user, invite_token: str | None = None):
    """Redireciona após login; aplica convite de banda se houver."""
    return _auth_setup_redirect(_auth_destination_path(user, invite_token))


def _redirect_after_signup(user, invite_token: str | None = None):
    """Redireciona após cadastro novo — passa pela URL de conversão do Google Ads."""
    dest = _auth_destination_path(user, invite_token)
    signup_page = url_for('auth.cadastro_concluido', next=dest)
    return _auth_setup_redirect(signup_page)


def _recuperar_senha_ctx(**extra):
    from email_service import is_configured as email_configured
    from whatsapp_service import is_configured as whatsapp_configured
    return dict(
        mail_configured=email_configured(),
        whatsapp_configured=whatsapp_configured(),
        recovery_available=email_configured() or whatsapp_configured(),
        **extra,
    )


@auth_bp.route('/recuperar-senha', methods=['GET', 'POST'])
def recuperar_senha():
    message = None
    message_kind = 'info'
    email_value = ''

    if request.method == 'POST':
        from auth_emails import send_password_reset_email, send_password_reset_whatsapp
        from email_service import is_configured as email_configured
        from whatsapp_service import is_configured as whatsapp_configured

        email_value = request.form.get('email', '').strip()
        if not email_value:
            message = 'Informe o e-mail cadastrado na sua conta.'
            message_kind = 'warning'
            return render_template(
                'recuperar_senha.html',
                **_recuperar_senha_ctx(message=message, message_kind=message_kind, email=email_value),
            )

        rate_key = f'reset-pwd:{request.remote_addr}:{email_value.lower()}'
        if not check_rate_limit(rate_key, max_attempts=5, window_sec=3600):
            message = 'Muitas tentativas. Aguarde uma hora e tente novamente.'
            message_kind = 'warning'
            return render_template(
                'recuperar_senha.html',
                **_recuperar_senha_ctx(message=message, message_kind=message_kind, email=email_value),
            )

        if not email_configured() and not whatsapp_configured():
            message = (
                'Recuperação de senha está temporariamente indisponível. '
                'Tente mais tarde ou fale com o suporte da banda.'
            )
            message_kind = 'warning'
            return render_template(
                'recuperar_senha.html',
                **_recuperar_senha_ctx(message=message, message_kind=message_kind, email=email_value),
            )

        user = get_user_by_email(email_value)
        if user:
            token = _password_reset_serializer().dumps(user['email'])
            sent_email = send_password_reset_email(user['email'], token) if email_configured() else False
            sent_wa = send_password_reset_whatsapp(user, token)
            if not sent_email and not sent_wa:
                current_app.logger.error(
                    'Falha ao enviar recuperação de senha para %s (e-mail=%s, whatsapp=%s)',
                    user['email'], sent_email, sent_wa,
                )
                message = (
                    'Não foi possível enviar o link agora. '
                    'Tente novamente em alguns minutos.'
                )
                message_kind = 'danger'
                return render_template(
                    'recuperar_senha.html',
                    **_recuperar_senha_ctx(message=message, message_kind=message_kind, email=email_value),
                )
            if not sent_wa and user.get('phone'):
                current_app.logger.warning(
                    'Recuperação enviada por e-mail, mas WhatsApp falhou para %s', user['email'],
                )

        message = (
            'Se o e-mail estiver cadastrado, enviamos um link de recuperação '
            '(válido por 1 hora) — por e-mail e, se houver WhatsApp no perfil, também por lá.'
        )
        message_kind = 'success'
        email_value = ''
        return render_template(
            'recuperar_senha.html',
            **_recuperar_senha_ctx(message=message, message_kind=message_kind, email=email_value),
        )

    return render_template('recuperar_senha.html', **_recuperar_senha_ctx())


@auth_bp.route('/reset/<token>', methods=['GET', 'POST'])
def reset_senha(token):
    message = None
    message_kind = 'info'
    s = _password_reset_serializer()
    try:
        email = s.loads(token, max_age=3600)
    except Exception:
        message = 'Link inválido ou expirado.'
        message_kind = 'warning'
        return render_template('reset_senha.html', message=message, message_kind=message_kind)

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        if not password or not confirm:
            message = 'Preencha todos os campos.'
            message_kind = 'warning'
        elif password != confirm:
            message = 'As senhas não conferem.'
            message_kind = 'warning'
        elif len(password) < MIN_PASSWORD_LEN:
            message = f'A senha deve ter no mínimo {MIN_PASSWORD_LEN} caracteres.'
            message_kind = 'warning'
        elif not update_user_password_by_email(email, password):
            message = 'Conta não encontrada. Solicite um novo link.'
            message_kind = 'warning'
        else:
            clear_rate_limit(f'reset-pwd:{request.remote_addr}:{email.lower()}')
            message = 'Senha redefinida com sucesso!'
            message_kind = 'success'
            return render_template('reset_senha.html', message=message, message_kind=message_kind)

    return render_template('reset_senha.html', message=message, message_kind=message_kind, token=token)

def login_required(f):
    """Decorator para rotas que requerem login"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            nxt = safe_redirect_path(request.path)
            if nxt:
                return redirect(url_for('auth.login', next=nxt))
            return redirect(url_for('auth.login'))
        endpoint = request.endpoint or ''
        if endpoint not in _SETUP_PROMPT_EXEMPT:
            nxt = safe_redirect_path(request.path) or url_for('dashboard')
            if _should_prompt_display_name():
                return redirect(url_for('auth.definir_nome', next=nxt))
            if _should_prompt_phone():
                return redirect(url_for('auth.definir_whatsapp', next=nxt))
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
    plano_intent = (request.args.get('plano') or request.form.get('plano') or '').strip().lower()
    if plano_intent in ('worship', 'pro', 'individual'):
        session['register_plano_intent'] = plano_intent
        session.modified = True
    elif not plano_intent:
        plano_intent = (session.get('register_plano_intent') or '').strip().lower()

    if 'user_id' in session:
        if band_id and apply_band_invite(session['user_id'], band_id):
            return redirect(url_for('bands.view', band_id=band_id))
        return redirect(url_for('dashboard'))

    def _register_ctx(**fields):
        return dict(
            invite_token=invite_token,
            invite_band=invite_band,
            plano_intent=plano_intent,
            **fields,
        )

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        display_name = request.form.get('display_name', '').strip()
        email = request.form.get('email', '').strip()
        phone_raw = request.form.get('phone', '').strip()
        whatsapp_notify = request.form.get('whatsapp_notify') == '1'
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        form_values = _register_ctx(
            username=username,
            display_name=display_name,
            email=email,
            phone=phone_raw,
            whatsapp_notify=whatsapp_notify,
        )
        
        if not username or not display_name or not email or not password:
            flash('Preencha usuário, nome, e-mail e senha', 'danger')
            return render_template('register.html', **form_values)

        if len(display_name) < 2:
            flash('Nome deve ter no mínimo 2 caracteres', 'danger')
            return render_template('register.html', **form_values)
        if len(display_name) > 60:
            flash('Nome deve ter no máximo 60 caracteres', 'danger')
            return render_template('register.html', **form_values)

        if phone_raw and not normalize_whatsapp_phone(phone_raw):
            flash('WhatsApp inválido. Use DDD + número (ex.: 85 99784-9547).', 'danger')
            return render_template('register.html', **form_values)
        
        if password != confirm:
            flash('Senhas não conferem', 'danger')
            return render_template('register.html', **form_values)
        
        if len(password) < MIN_PASSWORD_LEN:
            flash(f'Senha deve ter no mínimo {MIN_PASSWORD_LEN} caracteres', 'danger')
            return render_template('register.html', **form_values)
        
        if get_user_by_username(username):
            flash('Usuário já existe', 'danger')
            return render_template('register.html', **form_values)
        
        user_id = create_user(username, email, password, display_name=display_name)
        
        if not user_id:
            flash('Email já cadastrado', 'danger')
            return render_template('register.html', **form_values)

        update_user_profile(
            user_id,
            phone=phone_raw or None,
            whatsapp_notify=whatsapp_notify if phone_raw else False,
        )
        user = get_user(user_id)
        _login_user_session(user)
        from google_ads import mark_signup_conversion_pending
        mark_signup_conversion_pending()
        from onboarding_emails import registrar_onboarding_usuario
        registrar_onboarding_usuario(user_id)
        import admin_notifications as an
        an.user_registered(user_id)
        if invite_band:
            flash(f'Conta criada! Você já está na banda {invite_band["name"]}.', 'success')
        else:
            flash('Conta criada com sucesso!', 'success')
        return _redirect_after_signup(user, invite_token)

    return render_template(
        'register.html',
        invite_token=invite_token,
        invite_band=invite_band,
        plano_intent=plano_intent,
    )


@auth_bp.route('/cadastro-concluido')
@login_required
def cadastro_concluido():
    """
    Página de conversão Google Ads (inscrição).
    Só renderiza após cadastro novo; acessos diretos redirecionam sem contar conversão.
    """
    next_path = request.args.get('next', '')
    if not safe_redirect_path(next_path):
        next_path = url_for('dashboard')

    if not session.get('google_ads_funnel_pending'):
        return redirect(next_path)

    from db import get_user
    from google_ads import enhanced_user_data

    user = get_user(session.get('user_id'))
    return render_template(
        'cadastro_concluido.html',
        next_url=next_path,
        google_ads_enhanced_data=enhanced_user_data(user),
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
        login_id = (
            request.form.get('username')
            or request.form.get('email')
            or ''
        ).strip()
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

        flash('Usuário, e-mail ou senha incorretos', 'danger')

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
    from config import google_oauth_enabled

    if not google_oauth_enabled():
        flash(
            'Login com Google não está configurado no servidor. Use e-mail e senha ou contate o suporte.',
            'warning',
        )
        return redirect(url_for('auth.login'))
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
    new_signup = False

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
            from onboarding_emails import registrar_onboarding_usuario
            registrar_onboarding_usuario(user_id)
            import admin_notifications as an
            an.user_registered(user_id)
            new_signup = True

    _login_user_session(user)
    if new_signup:
        from google_ads import mark_signup_conversion_pending
        mark_signup_conversion_pending()
    flash(f'Bem-vindo, {session.get("display_name") or user["username"]}!', 'success')
    pending = session.pop('pending_band_invite', None)
    if new_signup:
        return _redirect_after_signup(user, pending)
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
        if _should_prompt_phone():
            return redirect(url_for('auth.definir_whatsapp', next=next_page))
        return redirect(next_page)

    if session.get('display_name'):
        if _should_prompt_phone():
            return redirect(url_for('auth.definir_whatsapp', next=next_page))
        return redirect(next_page)
    return render_template('definir_nome.html', next=next_page, suggested=session.get('username') or '')


@auth_bp.route('/whatsapp', methods=['GET', 'POST'])
@login_required
def definir_whatsapp():
    """Pede WhatsApp para contas sem telefone (usuários antigos no login)."""
    next_page = request.args.get('next') or url_for('dashboard')
    if not safe_redirect_path(next_page):
        next_page = url_for('dashboard')

    if request.args.get('pular') == '1':
        session['skip_phone_prompt'] = True
        session.modified = True
        flash('Você pode cadastrar o WhatsApp depois em Meu perfil.', 'info')
        return redirect(next_page)

    user = get_user(session['user_id'])
    if user and user_has_phone(user):
        return redirect(next_page)

    if request.method == 'POST':
        phone_raw = (request.form.get('phone') or '').strip()
        whatsapp_notify = request.form.get('whatsapp_notify') == '1'

        if not phone_raw:
            flash('Informe seu número de WhatsApp ou clique em Agora não.', 'warning')
            return render_template('definir_whatsapp.html', next=next_page)

        if not normalize_whatsapp_phone(phone_raw):
            flash('WhatsApp inválido. Use DDD + número (ex.: 85 99784-9547).', 'warning')
            return render_template('definir_whatsapp.html', next=next_page)

        update_user_profile(
            session['user_id'],
            phone=phone_raw,
            whatsapp_notify=whatsapp_notify,
        )
        session.pop('skip_phone_prompt', None)
        session.modified = True
        flash('WhatsApp cadastrado! Você receberá alertas da banda por aqui.', 'success')
        return redirect(next_page)

    return render_template('definir_whatsapp.html', next=next_page)


@auth_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    """Nome, WhatsApp e preferências de notificação."""
    user = get_user(session['user_id'])
    if not user:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('dashboard'))

    perfil_ctx = _perfil_template_context(user)

    if request.method == 'POST':
        form_section = (request.form.get('form_section') or 'profile').strip()
        blockout_action = (request.form.get('blockout_action') or '').strip()

        if blockout_action == 'add':
            from models_band_team import add_user_blockout
            bd = (request.form.get('block_date') or '').strip()
            note = (request.form.get('block_note') or '').strip()
            if add_user_blockout(session['user_id'], bd, note):
                flash('Data de indisponibilidade registrada.', 'success')
            else:
                flash('Data inválida ou já cadastrada.', 'warning')
            return redirect(url_for('auth.perfil'))
        if blockout_action == 'remove':
            from models_band_team import remove_user_blockout
            bd = (request.form.get('block_date') or '').strip()
            if bd:
                remove_user_blockout(session['user_id'], bd)
                flash('Indisponibilidade removida.', 'info')
            return redirect(url_for('auth.perfil'))

        if form_section == 'instruments':
            from user_instruments import normalize_instrument_ids, set_user_instruments

            selected = normalize_instrument_ids(request.form.getlist('instrument_ids'))
            set_user_instruments(session['user_id'], selected)
            flash('Instrumentos salvos.', 'success')
            return redirect(url_for('auth.perfil'))

        if form_section == 'notifications':
            from notification_prefs import NOTIFICATION_CATEGORIES

            push_notify = request.form.get('push_notify') == '1'
            email_notify = request.form.get('email_notify') == '1'
            whatsapp_notify = request.form.get('whatsapp_notify') == '1'
            prefs = {'categories': {}}
            for cat_id in NOTIFICATION_CATEGORIES:
                prefs['categories'][cat_id] = {
                    'push': request.form.get(f'notify_{cat_id}_push') == '1',
                    'email': request.form.get(f'notify_{cat_id}_email') == '1',
                    'whatsapp': request.form.get(f'notify_{cat_id}_whatsapp') == '1',
                }
            update_user_profile(
                session['user_id'],
                push_notify=push_notify,
                email_notify=email_notify,
                whatsapp_notify=whatsapp_notify if user.get('phone') else False,
                notification_prefs=prefs,
            )
            flash('Preferências de notificação salvas.', 'success')
            return redirect(url_for('auth.perfil'))

        nome = (request.form.get('display_name') or '').strip()
        phone_raw = (request.form.get('phone') or '').strip()

        if len(nome) < 2:
            flash('Digite um nome com pelo menos 2 caracteres.', 'warning')
            return render_template('perfil.html', **perfil_ctx)
        if len(nome) > 60:
            flash('Digite um nome com no máximo 60 caracteres.', 'warning')
            return render_template('perfil.html', **perfil_ctx)

        if phone_raw and not normalize_whatsapp_phone(phone_raw):
            flash('WhatsApp inválido. Use DDD + número (ex.: 11 99999-9999).', 'warning')
            return render_template('perfil.html', **perfil_ctx)

        update_user_profile(
            session['user_id'],
            display_name=nome,
            phone=phone_raw,
            whatsapp_notify=False if not phone_raw else None,
        )
        session['display_name'] = nome
        flash('Perfil atualizado.', 'success')
        return redirect(url_for('auth.perfil'))

    from models_band_team import list_user_blockouts
    perfil_ctx['blockouts'] = list_user_blockouts(session['user_id'])
    return render_template('perfil.html', **perfil_ctx)


def _perfil_template_context(user: dict) -> dict:
    from db import get_user_notification_prefs
    from notification_prefs import NOTIFICATION_CATEGORIES
    from push_notification_service import is_push_configured
    from user_instruments import instrument_catalog, list_user_instruments

    prefs = get_user_notification_prefs(user)
    user_instruments = list_user_instruments(user['id'])
    from db import get_owned_bands, get_user_bands
    from models_studio import list_studios_by_owner
    uid = user['id']
    has_bands = bool(get_owned_bands(uid) or get_user_bands(uid))
    has_studios = bool(list_studios_by_owner(uid))
    return {
        'user': user,
        'notification_categories': NOTIFICATION_CATEGORIES,
        'notification_prefs': prefs,
        'push_configured': is_push_configured(),
        'instrument_catalog': instrument_catalog(),
        'user_instruments': user_instruments,
        'user_instrument_ids': {item['id'] for item in user_instruments},
        'profile_has_bands': has_bands,
        'profile_has_studios': has_studios,
    }

