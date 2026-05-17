"""Telegram getUpdates → n8n internal Webhook bridge.

Заменяет webhook-flow `TelegramTrigger` в TestRag:
- long-poll Bot API getUpdates (offset acknowledgement)
- каждый update POST в `http://n8n:5678/webhook/tg-poll`
- НЕ нужен публичный URL/тоннель (закрывает known-issues.md #2 + #10)

Env:
  TELEGRAM_BOT_TOKEN          — required
  N8N_INTERNAL_WEBHOOK        — default http://n8n:5678/webhook/tg-poll
  POLL_TIMEOUT_S              — long-poll timeout (default 25)
  DELETE_WEBHOOK_ON_START     — `true`/`false` (default `true`). Если bot
                                шарится между проектами, выставить `false`
                                чтобы НЕ затирать чужой webhook на старте.
  OFFSET_STATE_PATH           — default /var/lib/tg-poll-bridge/offset.txt.
                                Volume mount в docker-compose для restart-
                                resilient «exactly-once» behaviour.
  LOG_LEVEL                   — default INFO
"""
from __future__ import annotations

import json
import logging
import os
import pathlib
import re
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
DELETE_WEBHOOK_ON_START = os.environ.get("DELETE_WEBHOOK_ON_START", "true").lower() == "true"
OFFSET_STATE_PATH = pathlib.Path(
    os.environ.get("OFFSET_STATE_PATH", "/var/lib/tg-poll-bridge/offset.txt")
)
ALLOWED_UPDATES = json.dumps(["message", "callback_query"])

_TOKEN_PATTERN = re.compile(re.escape(TG_TOKEN)) if TG_TOKEN else None


def _redact(text: str) -> str:
    """Redact TG token from any string before logging. urllib.error.HTTPError
    выводит URL в .geturl()/__str__; кому-то досталось через `repr(exc)` —
    замаскировать."""
    if not _TOKEN_PATTERN:
        return text
    return _TOKEN_PATTERN.sub("<TG_TOKEN>", text)


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


def maybe_delete_tg_webhook() -> None:
    if not DELETE_WEBHOOK_ON_START:
        log.info("DELETE_WEBHOOK_ON_START=false — skipping deleteWebhook")
        return
    try:
        info = _request(
            f"https://api.telegram.org/bot{TG_TOKEN}/getWebhookInfo",
            timeout=10,
        )
        current_url = (info.get("result") or {}).get("url", "")
        if not current_url:
            log.info("TG webhook already empty — polling mode safe to start")
            return
        log.info("TG webhook present (%s) — deleting", _redact(current_url))
        _request(
            f"https://api.telegram.org/bot{TG_TOKEN}/deleteWebhook",
            body={},
            timeout=10,
        )
        log.info("TG webhook deleted")
    except Exception as exc:
        log.warning("deleteWebhook prep failed (continuing): %s", _redact(str(exc)))


def _load_offset() -> int:
    try:
        return int(OFFSET_STATE_PATH.read_text(encoding="utf-8").strip() or "0")
    except FileNotFoundError:
        return 0
    except (ValueError, OSError) as exc:
        log.warning("offset state read failed (%s) — starting from 0", exc)
        return 0


def _save_offset(offset: int) -> None:
    try:
        OFFSET_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = OFFSET_STATE_PATH.with_suffix(".tmp")
        tmp.write_text(str(offset), encoding="utf-8")
        tmp.replace(OFFSET_STATE_PATH)
    except OSError as exc:
        log.warning("offset state write failed: %s", exc)


def _summarize(update: dict) -> str:
    if "callback_query" in update:
        return "callback"
    if "message" in update:
        return "message"
    return "other"


def forward(update: dict) -> bool:
    """Returns True iff n8n accepted update. Caller advances offset only on
    success — иначе at-most-once семантика теряет update при n8n flap."""
    try:
        _request(N8N_URL, body=update, timeout=15)
        log.info(
            "forwarded update_id=%s type=%s",
            update.get("update_id"),
            _summarize(update),
        )
        return True
    except urllib.error.HTTPError as exc:
        log.error(
            "forward HTTP %s for update_id=%s",
            exc.code,
            update.get("update_id"),
        )
        return False
    except Exception as exc:
        log.error(
            "forward failed for update_id=%s: %s",
            update.get("update_id"),
            _redact(str(exc)),
        )
        return False


def wait_for_n8n(max_wait_s: int = 120) -> None:
    """Опрос /webhook-test n8n или просто TCP-check. Bridge может стартовать
    раньше чем n8n зарегистрировал webhook path — backoff loop защищает от
    мгновенного потока 404."""
    start = time.time()
    while time.time() - start < max_wait_s:
        try:
            req = urllib.request.Request(N8N_URL, method="OPTIONS")
            with urllib.request.urlopen(req, timeout=5):
                pass
            log.info("n8n reachable at %s", N8N_URL)
            return
        except urllib.error.HTTPError as exc:
            # Любой HTTP response = n8n up (404/405 для OPTIONS на webhook ок)
            log.info("n8n responded HTTP %s — ready", exc.code)
            return
        except Exception as exc:
            log.info(
                "n8n not ready (%s) — retry in 3s",
                _redact(str(exc)),
            )
            time.sleep(3)
    log.warning("n8n still not reachable after %ss — starting poll-loop anyway", max_wait_s)


def poll_loop() -> None:
    offset = _load_offset()
    if offset:
        log.info("resumed from offset=%s", offset)
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
            log.warning(
                "getUpdates failed: %s — sleep %ss",
                _redact(str(exc)),
                backoff,
            )
            time.sleep(backoff)
            continue

        if not resp.get("ok"):
            log.warning("getUpdates not ok: %s", resp.get("description"))
            time.sleep(5)
            continue

        # At-least-once delivery: advance offset ТОЛЬКО на successful forward,
        # иначе same update retry'ится в следующем poll. Если n8n down — bridge
        # пилит retry-loop с backoff (TG side держит updates до 24h). Offset
        # persisted to disk → restart возобновляется без дубликатов.
        for update in resp.get("result", []):
            if not forward(update):
                time.sleep(2)
                break
            offset = update["update_id"] + 1
            _save_offset(offset)


def main() -> None:
    maybe_delete_tg_webhook()
    wait_for_n8n()
    log.info("polling Bot API → %s (timeout=%ss)", N8N_URL, POLL_TIMEOUT_S)
    poll_loop()


if __name__ == "__main__":
    main()
