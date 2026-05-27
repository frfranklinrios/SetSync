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

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicação
COPY . .

# Criar diretório de dados
RUN mkdir -p data

# Rodar com gunicorn em produção
EXPOSE 5000

CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]
