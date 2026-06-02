import requests
from flask import url_for, session, current_app
from security import external_url_for


def get_google_provider_cfg():
    """Obter configuração do Google"""
    return requests.get(current_app.config['GOOGLE_DISCOVERY_URL']).json()


def get_authorization_url(state: str | None = None):
    """Gerar URL de autorização do Google (com parâmetro state anti-CSRF)."""
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    if not state:
        state = make_oauth_state()

    request_uri = requests.Request("GET", authorization_endpoint, params={
        "client_id": current_app.config['GOOGLE_CLIENT_ID'],
        "redirect_uri": external_url_for("auth.google_callback"),
        "scope": "openid email profile",
        "response_type": "code",
        "prompt": "select_account",
        "state": state,
    }).prepare().url

    return request_uri


def handle_google_callback(code):
    """Processar callback do Google"""
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_payload = {
        "code": code,
        "client_id": current_app.config['GOOGLE_CLIENT_ID'],
        "client_secret": current_app.config['GOOGLE_CLIENT_SECRET'],
        "redirect_uri": external_url_for("auth.google_callback"),
        "grant_type": "authorization_code",
    }

    token_response = requests.post(token_endpoint, data=token_payload)

    if token_response.status_code != 200:
        return None

    tokens = token_response.json()
    id_token = tokens.get("id_token")

    if not id_token:
        return None

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    userinfo_response = requests.get(userinfo_endpoint, headers={
        "Authorization": f"Bearer {tokens['access_token']}"
    })

    if userinfo_response.status_code != 200:
        return None

    userinfo = userinfo_response.json()

    return {
        'id': userinfo.get('sub'),
        'email': userinfo.get('email'),
        'username': userinfo.get('email', '').split('@')[0],
        'name': userinfo.get('name'),
        'picture': userinfo.get('picture'),
    }
