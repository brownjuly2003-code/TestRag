"""E2E TG smoke: реальные нажатия кнопок через Telethon user account.
Тестирует N1 (follow-up) + N2 (🔁 Уточнить / 📖 Развернуть) + N3 (human handover) + N4 (reply threading)."""
from __future__ import annotations

import asyncio
import os
import re
import sys
from pathlib import Path

from telethon import TelegramClient
from telethon.errors import MessageNotModifiedError
from telethon.sessions import StringSession

def _load_env_from_file(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


_ENV_PATH = Path(os.environ.get("TG_MCP_ENV", "D:/MCP/telegram-mcp/.env"))
_ENV = _load_env_from_file(_ENV_PATH)


def _required(key_env: str, key_file: str) -> str:
    value = _ENV.get(key_file) or os.environ.get(key_env, "")
    if not value:
        raise SystemExit(
            f"Missing {key_env}/{key_file}. Set via env var или {_ENV_PATH}."
        )
    return value


API_ID = int(_required("TG_API_ID", "TELEGRAM_API_ID"))
API_HASH = _required("TG_API_HASH", "TELEGRAM_API_HASH")
SESSION = _required("TG_SESSION_STRING", "TELEGRAM_SESSION_STRING")

BOT = "@AIagentJu_bot"
TIMEOUT_S = 60


async def wait_for_new_message(client: TelegramClient, chat, after_id: int, max_wait: int = TIMEOUT_S):
    """Polls for bot's new message after `after_id`."""
    deadline = asyncio.get_event_loop().time() + max_wait
    while asyncio.get_event_loop().time() < deadline:
        msgs = await client.get_messages(chat, min_id=after_id, limit=20)
        for m in reversed(msgs):
            if m.sender_id != (await client.get_me()).id:
                return m
        await asyncio.sleep(2)
    return None


def render_buttons(msg) -> list[list[dict]]:
    if not msg or not msg.buttons:
        return []
    out = []
    for row in msg.buttons:
        row_out = []
        for btn in row:
            row_out.append({
                "text": btn.text,
                "data": btn.data.decode("utf-8") if isinstance(btn.data, (bytes, bytearray)) else btn.data,
            })
        out.append(row_out)
    return out


async def click_button_by_prefix(msg, prefix: str) -> str | None:
    if not msg.buttons:
        return None
    for row_idx, row in enumerate(msg.buttons):
        for col_idx, btn in enumerate(row):
            data = btn.data.decode("utf-8") if isinstance(btn.data, (bytes, bytearray)) else btn.data
            if data and data.startswith(prefix):
                try:
                    res = await btn.click()
                    return data
                except MessageNotModifiedError:
                    return data
    return None


async def main() -> int:
    async with TelegramClient(StringSession(SESSION), API_ID, API_HASH) as client:
        me = await client.get_me()
        print(f"Logged in as: {me.first_name} (id={me.id})")
        chat = await client.get_entity(BOT)
        print(f"Bot: {chat.username} (id={chat.id})")

        # Step 1: send the question
        q = "Что такое controlled zone?"
        sent = await client.send_message(chat, q)
        print(f"\n[1] SENT user msg_id={sent.id}: {q!r}")

        # Step 2: wait for bot reply with keyboard
        reply1 = await wait_for_new_message(client, chat, sent.id)
        if not reply1:
            print("FAIL: bot did not reply", file=sys.stderr)
            return 1
        print(f"[2] BOT reply msg_id={reply1.id} reply_to={reply1.reply_to_msg_id}")
        if reply1.reply_to_msg_id == sent.id:
            print("    ✓ N4: reply_to_message_id linked to user message")
        else:
            print(f"    ✗ N4: reply_to_msg_id={reply1.reply_to_msg_id}, expected {sent.id}")
        text_snippet = (reply1.message or "")[:120].replace("\n", " ")
        print(f"    text snippet: {text_snippet}")
        rows = render_buttons(reply1)
        print(f"    buttons rows: {len(rows)}")
        for i, row in enumerate(rows):
            for b in row:
                print(f"      row{i} '{b['text']}' → {b['data']}")

        # Step 2.5: N2 Quick-actions sanity — наличие 🔁 + 📖 (Sprint 6 #6)
        has_clarify = any(
            (b["data"] or "").startswith("clarify:")
            for row in rows for b in row
        )
        has_expand = any(
            (b["data"] or "").startswith("expand:")
            for row in rows for b in row
        )
        print(f"    {'✓' if has_clarify else '✗'} N2: 🔁 Уточнить button present")
        print(f"    {'✓' if has_expand else '✗'} N2: 📖 Развернуть button present")

        # Step 2.6: click 🔁 Уточнить → expect new bot reply with rerun (top_k=10)
        clarify_data = await click_button_by_prefix(reply1, "clarify:")
        if clarify_data:
            print(f"\n[2.6] CLICKED 🔁 Уточнить: {clarify_data}")
            reply_clarify = await wait_for_new_message(client, chat, reply1.id)
            if reply_clarify:
                snippet = (reply_clarify.message or "")[:140].replace("\n", " ")
                print(f"    BOT clarify reply msg_id={reply_clarify.id}: {snippet}")
                print("    ✓ N2: rerun answered")
            else:
                print("    ✗ N2: clarify reply timeout", file=sys.stderr)
        else:
            print("    WARN: 🔁 button missing — skipping", file=sys.stderr)
            reply_clarify = reply1

        # Step 2.7: click 📖 Развернуть на свежем reply (или fallback на reply1).
        # Expand reply — leaf-сообщение без keyboard (Send Direct Reply, plain HTML),
        # поэтому для followup-шага продолжаем работать с оригинальным reply1.
        anchor = reply_clarify or reply1
        expand_data = await click_button_by_prefix(anchor, "expand:")
        if expand_data:
            print(f"\n[2.7] CLICKED 📖 Развернуть: {expand_data}")
            reply_expand = await wait_for_new_message(client, chat, anchor.id)
            if reply_expand:
                snippet = (reply_expand.message or "")[:140].replace("\n", " ")
                print(f"    BOT expand reply msg_id={reply_expand.id}: {snippet}")
                print("    ✓ N2: chunk expanded")
            else:
                print("    ✗ N2: expand reply timeout", file=sys.stderr)
        else:
            print("    WARN: 📖 button missing — skipping", file=sys.stderr)

        # Step 3: click first 📎 follow-up button (N1)
        followup_data = await click_button_by_prefix(reply1, "followup:")
        if not followup_data:
            print("FAIL: no follow-up button in reply", file=sys.stderr)
            return 2
        print(f"\n[3] CLICKED follow-up: {followup_data}")

        # Step 4: wait for second bot reply
        reply2 = await wait_for_new_message(client, chat, reply1.id)
        if not reply2:
            print("FAIL: no second reply after follow-up click", file=sys.stderr)
            return 3
        print(f"[4] BOT 2nd reply msg_id={reply2.id} reply_to={reply2.reply_to_msg_id}")
        # reply_to should be the previous bot message (the one we clicked)
        if reply2.reply_to_msg_id == reply1.id:
            print("    ✓ N4: follow-up reply threads to clicked message")
        text_snippet = (reply2.message or "")[:140].replace("\n", " ")
        print(f"    text snippet: {text_snippet}")
        if "раздел" in (reply2.message or "").lower() or "подробнее" in (reply2.message or "").lower():
            print("    ✓ N1: follow-up question got a substantive answer")

        # Step 5: click 👎 to trigger feedback_bad_clarify
        bad_data = await click_button_by_prefix(reply2, "feedback:bad:")
        if not bad_data:
            print("WARN: no 👎 button on reply2", file=sys.stderr)
        else:
            print(f"\n[5] CLICKED 👎: {bad_data}")
            await asyncio.sleep(3)
            # Re-fetch reply2 to see edited reply markup
            reply2_refetch = await client.get_messages(chat, ids=reply2.id)
            new_rows = render_buttons(reply2_refetch)
            print(f"    after click, reply2 buttons rows: {len(new_rows)}")
            for row in new_rows:
                for b in row:
                    print(f"      '{b['text']}' → {b['data']}")

            # Step 6: click 🧑‍💼 Нужен человек (bad_human) — N3 trigger
            human_data = await click_button_by_prefix(reply2_refetch, "feedback:bad_human:")
            if human_data:
                print(f"\n[6] CLICKED 🧑‍💼: {human_data}")
                # Wait for HR/Legal ack — skip any split-part messages
                deadline = asyncio.get_event_loop().time() + 30
                ack = None
                last_seen = reply2.id
                while asyncio.get_event_loop().time() < deadline:
                    msgs = await client.get_messages(chat, min_id=last_seen, limit=10)
                    for m in reversed(msgs):
                        if m.sender_id == me.id:
                            continue
                        last_seen = max(last_seen, m.id)
                        text = m.message or ""
                        if "HR/Legal" in text and "ручную обработку" in text:
                            ack = m
                            break
                        print(f"    skipping intermediate msg_id={m.id}: {text[:80]!r}")
                    if ack:
                        break
                    await asyncio.sleep(2)
                if ack:
                    print(f"[7] ACK msg_id={ack.id}: {(ack.message or '')[:200]}")
                    print("    ✓ N3: human handover ack received")
                else:
                    print("    ✗ N3: handover ack not received within 30s")

        print("\nE2E DONE.")
        return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
