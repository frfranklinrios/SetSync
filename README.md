# SetSync

Gerenciador de cifras e setlists para bandas. Organize suas músicas, transpose acordes e execute o setlist ao vivo com o **Modo Tocar**.

## Funcionalidades

- **Bandas e membros** — crie bandas, convide músicos por e-mail, gerencie permissões
- **Cifras com destaque de acordes** — detecção automática de linhas de acorde vs. letra
- **Transposição automática** — suba ou desça o tom em tempo real, sem editar o arquivo
- **Setlist ordenado** — navegue entre músicas da banda com ← / →
- **Modo Tocar** — interface fullscreen para o palco
  - Barra de controle fixa com setlist lateral deslizante
  - Navegação por toque (swipe esquerda/direita) e teclado
  - Layout em **2 colunas** para cifras longas (sem precisar de scroll)
  - Auto-scroll configurável
  - Ajuste de tamanho de fonte
- **Dark / Light mode** — persiste entre sessões, acessível pelo navbar ou dentro do Modo Tocar (tecla `T`)
- **Login com Google OAuth** (opcional)

## Tech Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12 · Flask 3.0 |
| Banco de dados | SQLite 3 (sem ORM) |
| Auth | Flask-Login · Authlib (Google OAuth) |
| Frontend | Bootstrap 5.3 · Font Awesome 6.4 |
| Servidor | Gunicorn |
| Container | Docker / Podman |

## Rodando com Docker / Podman

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/setsync.git
cd setsync

# 2. Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com sua SECRET_KEY e credenciais do Google OAuth

# 3. Suba o container
docker compose up -d          # Docker
# ou
podman-compose up -d          # Podman rootless

# 4. Acesse em http://localhost:5000
```

## Rodando localmente (sem container)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edite .env
flask run
```

## Variáveis de ambiente

| Variável | Descrição |
|---|---|
| `SECRET_KEY` | Chave secreta do Flask (obrigatório) |
| `DATABASE_URL` | Caminho do SQLite (padrão: `sqlite:///data/banda.db`) |
| `FLASK_ENV` | `development` ou `production` |
| `GOOGLE_CLIENT_ID` | ID do app no Google Cloud Console (opcional) |
| `GOOGLE_CLIENT_SECRET` | Secret do app no Google Cloud Console (opcional) |

## Atalhos — Modo Tocar

| Tecla | Ação |
|---|---|
| `P` | Entrar no Modo Tocar |
| `Esc` | Sair do Modo Tocar |
| `← →` | Música anterior / próxima |
| `Espaço` | Ativar / pausar auto-scroll |
| `+ -` | Aumentar / diminuir fonte |
| `C` | Alternar layout 2 colunas |
| `S` | Abrir / fechar setlist |
| `T` | Alternar dark / light mode |
| Swipe ← → | Navegar músicas (touch) |

## Estrutura do projeto

```
├── app.py                  # Factory e registro de blueprints
├── config.py               # Configuração via .env
├── db.py                   # Acesso ao banco (SQLite puro)
├── util.py                 # Filtro Jinja2 highlight_chords
├── models.py               # Modelos Flask-Login
├── google_oauth.py         # Integração OAuth
├── blueprints/
│   ├── auth.py             # Login, registro, OAuth
│   ├── bands.py            # CRUD de bandas e membros
│   └── cifras.py           # CRUD de cifras + transposição
├── templates/
│   ├── index.html          # Base template (dark/light mode)
│   ├── cifras/view.html    # Visualização + Modo Tocar
│   └── ...
├── static/                 # Imagens e assets estáticos
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Licença

MIT
# SetSync
