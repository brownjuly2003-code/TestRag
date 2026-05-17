"""Telegram getUpdates → n8n internal Webhook bridge.

Заменяет webhook-flow `TelegramTrigger` в TestRag:
- long-poll Bot API getUpdates
- каждый update POST в `http://n8n:5678/webhook/tg-poll`
- НЕ нужен публичный URL/тоннель (закрывает known-issues.md #2 + #10)

Env:
  TELEGRAM_BOT_TOKEN     — required
  N8N_INTERNAL_WEBHOOK   — default http://n8n:5678/webhook/tg-poll
  POLL_TIMEOUT_S         — long-poll timeout (default 25)
  LOG_LEVEL              — default INFO
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("tg-poll-bridge")


TG_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TG_TOKEN:
    log.error("TELEGRAM_BOT_TOKEN env var is required")
    sys.exit(2)

N8N_URL = os.environ.get("N8N_INTERNAL_WEBHOOK", "http://n8n:5678/webhook/tg-poll")
POLL_TIMEOUT_S = int(os.environ.get("POLL_TIMEOUT_S", "25"))
ALLOWED_UPDATES = json.dumps(["message", "callback_query"])


def _request(
    url: str,
    *,
    body: dict | None = None,
    params: dict | None = None,
    timeout: int = 30,
) -> dict:
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    data: bytes | None = None
    headers: dict[str, str] = {}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    method = "POST" if data is not None else "GET"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))


def delete_tg_webhook() -> None:
    try:
        _request(f"https://api.telegram.org/bot{TG_TOKEN}/deleteWebhook", body={}, timeout=10)
        log.info("TG webhook deleted — polling mode active")
    except Exception as exc:
        log.warning("deleteWebhook failed (continuing): %s", exc)


def _summarize(update: dict) -> str:
    if "callback_query" in update:
        return "callback"
    if "message" in update:
        return "message"
    return "other"


def forward(update: dict) -> None:
    try:
        _request(N8N_URL, body=update, timeout=15)
        log.info(
            "forwarded update_id=%s type=%s",
            update.get("update_id"),
            _summarize(update),
        )
    except urllib.error.HTTPError as exc:
        log.error(
            "forward HTTP %s for update_id=%s",
            exc.code,
            update.get("update_id"),
        )
    except Exception as exc:
        log.error("forward failed for update_id=%s: %s", update.get("update_id"), exc)


def poll_loop() -> None:
    offset = 0
    consecutive_errors = 0
    while True:
        try:
            resp = _request(
                f"https://api.telegram.org/bot{TG_TOKEN}/getUpdates",
                params={
                    "offset": offset,
                    "timeout": POLL_TIMEOUT_S,
                    "allowed_updates": ALLOWED_UPDATES,
                },
                timeout=POLL_TIMEOUT_S + 10,
            )
            consecutive_errors = 0
        except urllib.error.HTTPError as exc:
            consecutive_errors += 1
            backoff = min(5 * consecutive_errors, 60)
            log.warning("getUpdates HTTP %s — sleep %ss", exc.code, backoff)
            time.sleep(backoff)
            continue
        except Exception as exc:
            consecutive_errors += 1
            backoff = min(5 * consecutive_errors, 60)
            log.warning("getUpdates failed: %s — sleep %ss", exc, backoff)
            time.sleep(backoff)
            continue

        if not resp.get("ok"):
            log.warning("getUpdates not ok: %s", resp.get("description"))
            time.sleep(5)
            continue

        for update in resp.get("result", []):
            forward(update)
            offset = update["update_id"] + 1


def main() -> None:
    delete_tg_webhook()
    log.info("polling Bot API → %s (timeout=%ss)", N8N_URL, POLL_TIMEOUT_S)
    poll_loop()


if __name__ == "__main__":
    main()
