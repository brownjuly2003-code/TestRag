"""Telegram answer formatting (port of n8n `Format Answer` JS Code node).

Sprint 8 #1 (issue #14 в `docs/known-issues.md`): порт 158 строк JS-кода из
`n8n/workflows/hr-legal-rag-workflow.json` (`Format Answer`) в Python.

Цель — убрать business logic из n8n JS, разрешить более жёсткий
`N8N_BLOCK_ENV_ACCESS_IN_NODE=true`, дать единую точку правки + native pytest
gate без необходимости в `node -e` shell-out.

Поведение 1:1 с JS-нодой (validated via parity tests в
`tests/test_format_answer.py`). Workflow обновится отдельным шагом: HTTP-нода
`POST /format-answer` заменит Code node. До миграции оба тракта живут
параллельно; pin-тесты `test_n8n_workflow.py::test_format_answer_*`
продолжают валидировать JS-копию.

Endpoint: `POST /format-answer` (см. `app/main.py`).
"""
from __future__ import annotations

import html
import re
from dataclasses import dataclass
from typing import Any


TG_MAX_PART = 4000  # запас от лимита sendMessage (4096) под `<i>часть N/M</i>` суффикс
_BALANCE_TAGS = ("b", "code", "i")

_REFUSAL_PATTERNS = (
    re.compile(r"данных недостаточно", re.IGNORECASE),
    re.compile(r"не нашел? в (предоставленных )?источниках", re.IGNORECASE),
    re.compile(r"не содерж[аи]т (информации|ответа)", re.IGNORECASE),
    re.compile(r"отсутствует определение", re.IGNORECASE),
    re.compile(r"в (корпусе|базе знаний) нет", re.IGNORECASE),
    re.compile(r"не нашел подходящих", re.IGNORECASE),
)


def _escape_html(s: Any) -> str:
    return html.escape("" if s is None else str(s), quote=False)


_CODE_RE = re.compile(r"`([^`\n]+)`")
_BOLD_RE = re.compile(r"\*\*([^*\n]+?)\*\*")
_LIST_DASH_RE = re.compile(r"^- ", re.MULTILINE)
_LIST_STAR_RE = re.compile(r"^\* ", re.MULTILINE)


def md_to_html(s: str) -> str:
    """Mistral возвращает MarkdownV1. TG бот рендерит parse_mode=HTML.

    Покрываем три самых частых паттерна: inline `code`, **bold**, маркированные
    списки `-`/`*`. Италик `*X*` намеренно НЕ конвертируем (ложные срабатывания
    на арифметике `5*8`). Ссылки `[label](url)` и `# headers` тоже игнорируем —
    модель в этом контексте их не выдаёт.
    """
    s = _CODE_RE.sub(r"<code>\1</code>", s)
    s = _BOLD_RE.sub(r"<b>\1</b>", s)
    s = _LIST_DASH_RE.sub("• ", s)
    s = _LIST_STAR_RE.sub("• ", s)
    return s


def balance_tags(s: str) -> str:
    """Если split разрывает <b>...</b> между частями, дозакрыть/доткрыть."""
    for tag in _BALANCE_TAGS:
        opens = s.count(f"<{tag}>")
        closes = s.count(f"</{tag}>")
        if opens > closes:
            s = s + f"</{tag}>" * (opens - closes)
        elif closes > opens:
            s = f"<{tag}>" * (closes - opens) + s
    return s


def confidence_band(conf: float | None) -> str:
    """Sprint 8 #2 (codex-audit#5.2): banding logic, чтобы API и UI читали
    из одной точки. Раньше n8n интерпретировал confidence в чипы автономно —
    drift между backend refusal policy и UI band'ами был возможен.

    `unknown` — для confidence=None / non-numeric. `none` — для conf == 0
    (явный refusal). `low/medium/high` пороги совпадают с UI-чипами.
    """
    if conf is None:
        return "unknown"
    if conf >= 0.7:
        return "high"
    if conf >= 0.4:
        return "medium"
    if conf > 0:
        return "low"
    return "none"


_BAND_CHIP_TEXT: dict[str, str] = {
    "high": "🟢 <b>Высокая уверенность</b>",
    "medium": "🟡 <b>Средняя уверенность</b> — сверьтесь с источником",
    "low": "🟠 <b>Низкая уверенность</b> — рассмотрите 🧑‍💼 эскалацию",
    "none": "",
    "unknown": "",
}


def confidence_chip(conf: float | None) -> str:
    """Chip-текст для TG-сообщения. Внутри — `confidence_band` для UI/API parity."""
    return _BAND_CHIP_TEXT.get(confidence_band(conf), "")


def looks_refusal(text: str) -> bool:
    return any(p.search(text) for p in _REFUSAL_PATTERNS)


_SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def split_into_parts(full: str, max_len: int = TG_MAX_PART) -> list[str]:
    """Hierarchical split: by paragraphs (`\\n\\n`), затем sentences, иначе hard slice.

    Возвращает части ≤ max_len с дозакрытыми HTML-тегами в каждой (via `balance_tags`).
    """
    if len(full) <= max_len:
        return [full]
    parts: list[str] = []
    current = ""

    def _flush() -> None:
        nonlocal current
        if current:
            parts.append(current)
            current = ""

    for para in full.split("\n\n"):
        candidate = f"{current}\n\n{para}" if current else para
        if len(candidate) <= max_len:
            current = candidate
            continue
        _flush()
        if len(para) <= max_len:
            current = para
            continue
        sentences = _SENT_SPLIT_RE.split(para)
        s_cur = ""
        for sent in sentences:
            s_cand = f"{s_cur} {sent}" if s_cur else sent
            if len(s_cand) <= max_len:
                s_cur = s_cand
                continue
            if s_cur:
                parts.append(s_cur)
                s_cur = ""
            if len(sent) > max_len:
                for i in range(0, len(sent), max_len):
                    parts.append(sent[i : i + max_len])
            else:
                s_cur = sent
        if s_cur:
            parts.append(s_cur)
    _flush()
    return [balance_tags(p) for p in parts]


def _truncate(s: Any, max_len: int) -> str:
    text = "" if s is None else str(s)
    return text if len(text) <= max_len else text[: max_len - 1] + "…"


_PLURAL_FORMS = (
    "релевантный документ",
    "релевантных документа",
    "релевантных документов",
)


def plural_ru_docs(n: int) -> str:
    mod10 = n % 10
    mod100 = n % 100
    if mod10 == 1 and mod100 != 11:
        return _PLURAL_FORMS[0]
    if 2 <= mod10 <= 4 and (mod100 < 12 or mod100 > 14):
        return _PLURAL_FORMS[1]
    return _PLURAL_FORMS[2]


@dataclass(frozen=True)
class _DedupedSource:
    file: str
    section: str | None
    chunk_id: str | None
    score: float | None
    original_idx: int


def _dedup_sources(sources: list[dict[str, Any]]) -> list[_DedupedSource]:
    seen: set[str] = set()
    deduped: list[_DedupedSource] = []
    for idx, src in enumerate(sources):
        file = src.get("file") or src.get("chunk_id") or ""
        if file and file in seen:
            continue
        seen.add(file)
        deduped.append(
            _DedupedSource(
                file=src.get("file") or src.get("chunk_id") or "unknown",
                section=src.get("section"),
                chunk_id=src.get("chunk_id"),
                score=src.get("score"),
                original_idx=idx,
            )
        )
    return deduped


def _build_keyboard(
    deduped: list[_DedupedSource],
    request_log_id: str,
) -> dict[str, Any] | None:
    """Inline keyboard 3 rows (followup до 2 / quick-actions / feedback).

    Полная parity с JS: первая строка — followup-кнопки top-2 источников (если
    есть). Вторая — `🔁 Уточнить` + `📖 Развернуть` (последняя только если
    source[0] существует). Третья — `👍 Полезно` / `👎 Неточно`.
    """
    if not request_log_id:
        return None
    rows: list[list[dict[str, str]]] = []

    followup_row = [
        {
            "text": f"📎 {_truncate(s.section or s.file or 'подробнее', 32)}",
            "callback_data": f"followup:{s.original_idx}:{request_log_id}",
        }
        for s in deduped[:2]
    ]
    if followup_row:
        rows.append(followup_row)

    has_sources = bool(deduped)
    quick_row: list[dict[str, str]] = [
        {"text": "🔁 Уточнить", "callback_data": f"clarify:{request_log_id}"},
    ]
    if has_sources:
        quick_row.append(
            {"text": "📖 Развернуть", "callback_data": f"expand:0:{request_log_id}"}
        )
    rows.append(quick_row)

    rows.append(
        [
            {"text": "👍 Полезно", "callback_data": f"feedback:good:{request_log_id}"},
            {"text": "👎 Неточно", "callback_data": f"feedback:bad:{request_log_id}"},
        ]
    )
    return {"inline_keyboard": rows}


def format_answer(
    *,
    answer: str | None,
    confidence: float | None,
    refused: bool,
    sources: list[dict[str, Any]] | None,
    request_log_id: str,
    chat_id: int | str,
    user_message_id: int | None = None,
) -> list[dict[str, Any]]:
    """Возвращает массив payload'ов, готовых к Telegram sendMessage.

    Каждый payload:
        chat_id, text, request_log_id, is_last, part_index, part_total,
        inline_keyboard (только на is_last=True), reply_to_message_id
        (только на первой части).
    """
    sources = sources or []
    raw_answer = answer or ""
    deduped = _dedup_sources(sources)

    is_refusal = bool(refused) or looks_refusal(raw_answer)
    chip = "" if is_refusal else confidence_chip(confidence)

    answer_html = md_to_html(_escape_html(raw_answer))
    count = len(deduped)
    if count > 0:
        summary = f"Найдено {count} {plural_ru_docs(count)}."
    else:
        summary = "По базе знаний не найдено подходящих документов."

    sources_lines = [
        f"{i + 1}. <code>{_escape_html(s.file)}</code> — "
        f"{_escape_html(s.section or 'раздел не указан')}"
        for i, s in enumerate(deduped)
    ]
    sources_block = "\n".join(sources_lines)

    if is_refusal:
        next_steps = (
            "\n\n<b>Что делать дальше:</b>\n"
            "• уточните вопрос конкретнее (термины, документ, дата)\n"
            "• посмотрите покрытие — /docs\n"
            "• для эскалации к HR/Legal — кнопка 🧑‍💼 ниже"
        )
        sources_header = "Ближайшие документы (вне ответа):" if count > 0 else None
    else:
        next_steps = ""
        sources_header = "Источники:" if count > 0 else None

    header = f"{chip}\n\n" if chip else ""
    if count > 0 and sources_header:
        sources_section = f"\n\n{summary}\n\n{sources_header}\n{sources_block}"
    else:
        sources_section = f"\n\n{summary}"

    full_text = f"{header}{answer_html}{next_steps}{sources_section}"
    parts = split_into_parts(full_text, TG_MAX_PART)
    total = len(parts)

    keyboard = _build_keyboard(deduped, request_log_id) if request_log_id else None

    out: list[dict[str, Any]] = []
    for i, text in enumerate(parts):
        is_last = i == total - 1
        decorated = f"{text}\n\n<i>часть {i + 1}/{total}</i>" if total > 1 else text
        out.append(
            {
                "chat_id": chat_id,
                "text": decorated,
                "request_log_id": request_log_id,
                "is_last": is_last,
                "part_index": i + 1,
                "part_total": total,
                "inline_keyboard": keyboard if is_last else None,
                "reply_to_message_id": user_message_id if i == 0 else None,
            }
        )
    return out
