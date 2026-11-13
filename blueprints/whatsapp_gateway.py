"""Gateway e Roteador Central de Webhooks do WhatsApp.

Compartilha uma única instância da Evolution API conectada entre
os ecossistemas Uníssono (música, bandas, ensaios) e Finanças.tec (gastos, finanças pessoais/casal).

Arquitetura:
- Recebe eventos da Evolution API em /api/whatsapp/gateway (sem CSRF).
- Responde 200 OK imediatamente para não prender a fila da Evolution API.
- Inspeciona o payload assincronamente (intenção, comandos, mídias, remetentes).
- Encaminha mensagens financeiras/mídias para financas_backend_core.
- Roteia mensagens musicais/de bandas para o fluxo do Uníssono.
- Fornece endpoint de telemetria /api/whatsapp/gateway/status.
"""

from __future__ import annotations

import concurrent.futures
import json
import logging
import os
import re
import time
from typing import Any

from flask import Blueprint, jsonify, request
import requests

logger = logging.getLogger("setsync.whatsapp.gateway")

whatsapp_gateway_bp = Blueprint("whatsapp_gateway", __name__)

_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=5, thread_name_prefix="wa_gw_worker")

# Métricas em memória para telemetria
_METRICS: dict[str, Any] = {
    "total_received": 0,
    "routed_financas": 0,
    "routed_unissono": 0,
    "routed_both": 0,
    "ignored_from_me": 0,
    "last_event_time": None,
    "last_event_type": None,
    "errors": 0,
}

# Configurações do Gateway
def get_financas_webhook_url() -> str:
    return (
        os.getenv("FINANCAS_WEBHOOK_URL")
        or "http://financas_backend_core:8080/api/v1/webhook/whatsapp"
    ).strip()


def get_routing_mode() -> str:
    """Modos: 'smart' (analisa intenção e remetente) ou 'fanout' (broadcast seguro)."""
    return (os.getenv("WHATSAPP_ROUTING_MODE") or "smart").strip().lower()


def get_financas_phones() -> set[str]:
    """Números conhecidos de finanças configurados via env (ex: '5511999999999,5511888888888')."""
    raw = os.getenv("FINANCAS_WHATSAPP_NUMBERS") or ""
    return {re.sub(r"\D", "", p) for p in raw.split(",") if re.sub(r"\D", "", p)}


# Palavras-chave e padrões de Finanças
_FINANCAS_KEYWORDS = {
    "r$", "reais", "centavos", "gastei", "paguei", "comprei", "custou", "pago",
    "transferi", "pix", "cartao", "cartão", "debito", "débito", "credito", "crédito",
    "almoco", "almoço", "jantar", "lanche", "mercado", "supermercado", "padaria",
    "farmacia", "farmácia", "posto", "gasolina", "combustivel", "combustível",
    "uber", "99", "taxi", "táxi", "aluguel", "condominio", "condomínio", "fatura",
    "boleto", "salario", "salário", "saldo", "extrato", "despesa", "receita",
    "renda", "investimento", "comprovante", "recibo", "nota", "cupom",
    "/gasto", "/financas", "/saldo", "#fin", "#gasto", "#financas",
}

# Expressões regulares financeiras (ex: '50 mercado', '35,90 padaria', '20 reais')
_FINANCAS_VALUE_REGEX = re.compile(
    r"(?:\b\d+([.,]\d{1,2})?\s*(?:reais|conto|pila)\b)|"
    r"(?:r\$\s*\d+([.,]\d{1,2})?)|"
    r"(?:^\s*\d+([.,]\d{1,2})?\s+[a-zA-ZáéíóúãõçÁÉÍÓÚÃÕÇ]+)",
    re.IGNORECASE,
)

# Palavras-chave do Uníssono
_UNISSONO_KEYWORDS = {
    "/setlist", "/musica", "/música", "/cifra", "/tom", "/ensaio", "/banda",
    "/agenda", "/estudio", "/estudios", "/show", "/repertorio", "/repertório",
    "/escala", "unissono", "uníssono", "setsync", "#unissono", "#setsync",
    "repertorio", "repertório", "cifras", "cifra", "afinacao", "afinação",
    "metronomo", "metrônomo", "ensaio", "setlist", "escala",
}



def classify_message(payload: dict[str, Any]) -> dict[str, Any]:
    """Inspeciona o payload recebido da Evolution API e decide destinos."""
    event = (payload.get("event") or "").lower()
    instance = payload.get("instance") or ""
    data = payload.get("data") or {}
    if isinstance(data, list) and data:
        data = data[0]

    if not isinstance(data, dict):
        return {
            "is_financas": False,
            "is_unissono": False,
            "reasons": ["invalid_data"],
            "sender": "",
            "text": "",
            "has_media": False,
            "from_me": False,
            "event": event,
        }

    key = data.get("key") or {}
    remote_jid = str(key.get("remoteJid") or "")
    sender_digits = re.sub(r"\D", "", remote_jid.split("@")[0] if "@" in remote_jid else remote_jid)
    from_me = bool(key.get("fromMe"))
    message = data.get("message") or {}

    # Extrai texto de múltiplos formatos
    text = ""
    if isinstance(message, dict):
        text = (
            message.get("conversation")
            or (message.get("extendedTextMessage") or {}).get("text")
            or (message.get("imageMessage") or {}).get("caption")
            or (message.get("videoMessage") or {}).get("caption")
            or (message.get("documentMessage") or {}).get("caption")
            or ""
        ).strip()

    media_types = ("audioMessage", "imageMessage", "documentMessage", "videoMessage", "stickerMessage")
    has_media = isinstance(message, dict) and any(m in message for m in media_types)

    reasons_financas: list[str] = []
    reasons_unissono: list[str] = []

    # 1. Checa remetente pré-cadastrado de Finanças
    financas_phones = get_financas_phones()
    if sender_digits and sender_digits in financas_phones:
        reasons_financas.append("known_financas_sender")

    # 2. Mídias (áudio para transcrição IA ou fotos de comprovante OCR) vão para Finanças
    if has_media:
        reasons_financas.append("media_payload")

    # 3. Análise textual
    lower_text = text.lower()
    words = set(re.findall(r"[/\#\w]+", lower_text))

    matched_fin_kw = words.intersection(_FINANCAS_KEYWORDS)
    if matched_fin_kw:
        reasons_financas.append(f"financas_kw:{','.join(list(matched_fin_kw)[:3])}")

    if _FINANCAS_VALUE_REGEX.search(lower_text):
        reasons_financas.append("monetary_value_pattern")

    matched_uni_kw = words.intersection(_UNISSONO_KEYWORDS)
    if matched_uni_kw:
        reasons_unissono.append(f"unissono_kw:{','.join(list(matched_uni_kw)[:3])}")

    # Modo de roteamento
    mode = get_routing_mode()
    is_financas = False
    is_unissono = False

    if mode == "fanout":
        is_financas = True
        is_unissono = True
    else:
        # Modo 'smart':
        if reasons_financas:
            is_financas = True
        if reasons_unissono:
            is_unissono = True

        # Se não casou com nenhum, mas parece mensagem de usuário comum recebida:
        # No finanças, o backend descarta se o número não existir na base dele.
        # Encaminhamos como fallback se houver texto com dígitos ou mídia.
        if not is_financas and not is_unissono and text:
            if re.search(r"\d", text):
                is_financas = True
                reasons_financas.append("numeric_fallback")

    return {
        "is_financas": is_financas,
        "is_unissono": is_unissono,
        "reasons_financas": reasons_financas,
        "reasons_unissono": reasons_unissono,
        "sender": sender_digits,
        "text": text,
        "has_media": has_media,
        "from_me": from_me,
        "event": event,
        "instance": instance,
    }


def _forward_to_financas(payload: dict[str, Any]) -> bool:
    """Encaminha o payload integral da Evolution API para o backend de Finanças."""
    target_url = get_financas_webhook_url()
    try:
        t0 = time.perf_counter()
        resp = requests.post(
            target_url,
            json=payload,
            headers={"Content-Type": "application/json", "X-Forwarded-By": "unissono-gateway"},
            timeout=10,
        )
        duration_ms = int((time.perf_counter() - t0) * 1000)
        if resp.ok:
            logger.info("Encaminhado com sucesso para Finanças (%s ms, status %s)", duration_ms, resp.status_code)
            return True
        logger.warning(
            "Finanças respondeu erro %s em %s ms: %s",
            resp.status_code,
            duration_ms,
            resp.text[:200],
        )
        return False
    except requests.exceptions.RequestException as exc:
        logger.warning("Falha ao encaminhar webhook para Finanças: %s", exc)
        return False
    except Exception:
        logger.exception("Erro inesperado ao despachar para Finanças")
        return False


def _process_unissono_event(payload: dict[str, Any], meta: dict[str, Any]) -> bool:
    """Processa comandos ou respostas no contexto musical do Uníssono."""
    text = meta.get("text") or ""
    sender = meta.get("sender") or ""
    logger.info("Processamento interno Uníssono: sender=%s text=%s", sender, text[:60])
    # Futuros gatilhos de repertório e bot musical podem ser plugados diretamente aqui
    return True


def _async_dispatch(payload: dict[str, Any], meta: dict[str, Any]) -> None:
    """Executado na pool de threads sem bloquear o retorno HTTP da Evolution API."""
    global _METRICS
    try:
        if meta.get("from_me"):
            _METRICS["ignored_from_me"] += 1
            # Mensagens originadas por nós mesmos não precisam acionar IA financeira
            return

        is_fin = meta.get("is_financas")
        is_uni = meta.get("is_unissono")

        if is_fin and is_uni:
            _METRICS["routed_both"] += 1
        elif is_fin:
            _METRICS["routed_financas"] += 1
        elif is_uni:
            _METRICS["routed_unissono"] += 1

        if is_fin:
            _forward_to_financas(payload)

        if is_uni:
            _process_unissono_event(payload, meta)

    except Exception:
        _METRICS["errors"] += 1
        logger.exception("Erro no processamento assíncrono do Gateway WhatsApp")


@whatsapp_gateway_bp.route("/api/whatsapp/gateway", methods=["POST"])
def gateway_webhook():
    """Recebe webhooks da Evolution API e despacha para os apps configurados."""
    global _METRICS
    try:
        raw_data = request.get_data()
        if not raw_data:
            return jsonify({"ok": False, "error": "Empty payload"}), 400

        payload = request.get_json(silent=True) or {}
        _METRICS["total_received"] += 1
        _METRICS["last_event_time"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        _METRICS["last_event_type"] = payload.get("event")

        # Classificação rápida
        meta = classify_message(payload)

        # Despacho assíncrono para liberar a Evolution API imediatamente (< 50ms)
        _EXECUTOR.submit(_async_dispatch, payload, meta)

        return jsonify({
            "status": "received",
            "event": meta.get("event"),
            "routed": {
                "financas": meta.get("is_financas"),
                "unissono": meta.get("is_unissono"),
            },
        }), 200

    except Exception as exc:
        _METRICS["errors"] += 1
        logger.exception("Erro crítico no endpoint do gateway")
        return jsonify({"ok": False, "error": str(exc)}), 500


@whatsapp_gateway_bp.route("/api/whatsapp/gateway/status", methods=["GET"])
def gateway_status():
    """Retorna estado e telemetria do Gateway WhatsApp compartilhado."""
    financas_url = get_financas_webhook_url()
    financas_reachable = False
    try:
        # Ping rápido no endpoint de finanças
        resp = requests.get(financas_url.replace("/webhook/whatsapp", "/health"), timeout=1.5)
        financas_reachable = resp.ok or resp.status_code < 500
    except Exception:
        financas_reachable = False

    return jsonify({
        "gateway": "active",
        "routing_mode": get_routing_mode(),
        "financas_webhook_url": financas_url,
        "financas_reachable": financas_reachable,
        "financas_configured_phones": list(get_financas_phones()),
        "metrics": _METRICS,
    }), 200
