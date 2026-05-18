"""Telegram «summary» formatters (port of n8n `Format History` / `Format Docs`).

Sprint 8 #2 (codex-audit#5.1): порт JS Code-узлов в Python. n8n-нода теперь
вызывает `/tg/format-history` / `/tg/format-docs` через HTTP — формирование
текста перестаёт быть JS-логикой в workflow.

Behavior 1:1 с JS-копией. Parity-coverage в `tests/test_tg_format.py`.
"""
from __future__ import annotations

import html
from typing import Any


def _escape(s: Any) -> str:
    return html.escape("" if s is None else str(s), quote=False)


def _plural_history(n: int) -> tuple[str, str]:
    """Returns (prefix, noun) для заголовка истории. JS parity."""
    mod10 = n % 10
    mod100 = n % 100
    if mod10 == 1 and mod100 != 11:
        return ("Последний", "запрос")
    if 2 <= mod10 <= 4 and (mod100 < 12 or mod100 > 14):
        return ("Последние", "запроса")
    return ("Последние", "запросов")


def format_history(items: list[dict[str, Any]]) -> str:
    """История запросов пользователя для команды /history.

    Каждая запись: порядковый номер, дата (YYYY-MM-DD HH:MM), [отказ] tag для
    refused=True, обрезанный текст вопроса (≤120 chars) в <code>.
    """
    if not items:
        return "История запросов пуста. Задайте первый вопрос — он попадёт в /history."
    lines: list[str] = []
    for i, it in enumerate(items):
        question = _escape((it.get("question") or ""))[:120]
        when = (it.get("created_at") or "")[:16].replace("T", " ")
        tag = " [отказ]" if it.get("refused") else ""
        lines.append(f"{i + 1}. <b>{_escape(when)}</b>{tag}\n   <code>{question}</code>")
    prefix, noun = _plural_history(len(items))
    body = "\n\n".join(lines)
    return f"<b>{prefix} {len(items)} {noun}:</b>\n\n{body}"


def format_docs(categories: list[dict[str, Any]], total_docs: int) -> str:
    """Состав корпуса для команды /docs."""
    if not categories:
        return "Корпус пуст или не загружен."
    lines: list[str] = []
    for cat in categories:
        label = _escape(cat.get("label"))
        count = cat.get("doc_count", 0)
        samples_raw = (cat.get("sample_files") or [])[:2]
        samples = ", ".join(f"<code>{_escape(f)}</code>" for f in samples_raw)
        tail = f" — например {samples}" if samples else ""
        lines.append(f"• <b>{label}</b> ({count}){tail}")
    body = "\n".join(lines)
    return (
        f"<b>Корпус знаний: {total_docs} документов</b>\n\n"
        f"{body}\n\n"
        "<i>Задайте вопрос по любой категории — ассистент найдёт релевантные документы "
        "и сошлётся на конкретные разделы.</i>"
    )
