FROM python:3.12-slim

WORKDIR /app

# ffmpeg: áudio do importador | Deno: desafios JS do YouTube (yt-dlp EJS)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    unzip \
    ffmpeg \
    && curl -fsSL https://deno.land/install.sh | DENO_INSTALL=/usr/local sh \
    && rm -rf /var/lib/apt/lists/* \
    && deno --version \
    && ffmpeg -version | head -1

# Copiar requirements e instalar Chromium do Playwright (importador Cifra Club)
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && playwright install --with-deps chromium

# Copiar aplicação
COPY . .

# Criar diretório de dados
RUN mkdir -p data

# Rodar com gunicorn em produção
EXPOSE 5000

CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]
