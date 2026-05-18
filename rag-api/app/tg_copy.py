"""Telegram-bot copy blocks (greeting/help/clear).

Sprint 6 #1: вынесены из n8n Whitelist Code node в rag-api для:
1) убрать business logic из n8n JS-кода (Issue #14 из kimi_audit);
2) разрешить `N8N_BLOCK_ENV_ACCESS_IN_NODE=true`;
3) дать единую точку правки copy без re-import workflow.
"""
from __future__ import annotations


GREETING_TEXT = (
    "<b>TestRag — HR/Legal RAG-ассистент</b>\n\n"
    "Отвечаю на вопросы по корпоративным документам: HR-политики, кадровые шаблоны, "
    "договоры, претензии, авиагрузовая логистика. "
    "Каждый ответ сопровождается ссылками на конкретные источники и оценкой уверенности.\n\n"
    "<b>Попробуйте:</b>\n"
    "• Что такое controlled zone?\n"
    "• Какие документы нужны для отправки dangerous goods авиатранспортом?\n"
    "• Какие основания для досрочного расторжения трудового договора?\n\n"
    "<b>Команды:</b> /help — справка · /docs — что в корпусе · /history — мои запросы · /clear — про сохранение состояния"
)

HELP_TEXT = (
    "<b>Что я умею</b>\n"
    "• Отвечаю на вопросы по HR, кадровому делопроизводству, договорам, претензиям, авиагрузовой логистике "
    "(AWB/MAWB/HAWB, controlled zone, dangerous goods, GHA, ULD, cutoff).\n"
    "• Каждый ответ опирается на конкретные документы корпуса со ссылкой на раздел.\n"
    "• Уверенность ответа маркируется как 🟢 высокая, 🟡 средняя или 🟠 низкая.\n"
    "• 👍/👎 под ответом — оценка, попадает в очередь ревью.\n"
    "• 📎 — дозапрос подробностей по конкретному источнику.\n"
    "• 🧑‍💼 — эскалация к HR/Legal (последние 5 запросов прилагаются).\n\n"
    "<b>Примеры вопросов</b>\n"
    "• Что такое controlled zone?\n"
    "• Какие документы нужны для отправки dangerous goods авиатранспортом?\n"
    "• Какие основания для досрочного расторжения трудового договора?\n"
    "• Какой испытательный срок по ТК РФ?\n"
    "• Как составить претензию контрагенту?\n\n"
    "<b>Команды</b>\n"
    "/help — эта справка\n"
    "/docs — категории и состав корпуса\n"
    "/history — последние 5 запросов\n"
    "/clear — про сохранение состояния"
)

CLEAR_TEXT = (
    "<b>Контекст не сохраняется</b> — каждый ответ автономен и не зависит от предыдущих сообщений. "
    "Если нужно сослаться на старый запрос — используйте /history."
)

EMPTY_INPUT_TEXT = (
    "Пока понимаю только текстовые вопросы. Задайте вопрос по HR, юридическим "
    "или договорным документам одним сообщением."
)

THANKS_TEXT = (
    "Пожалуйста. Если нужен разбор по HR/legal-документам, "
    "задайте вопрос одним сообщением."
)

UNKNOWN_FEEDBACK_REASON_TEXT = "Неизвестная причина обратной связи."
UNKNOWN_FEEDBACK_TEXT = "Неизвестная команда обратной связи."
UNRECOGNIZED_FOLLOWUP_TEXT = "Не удалось распознать запрос на уточнение. Задайте вопрос текстом."

# Sprint 8 #2 (codex-audit#5.1): port Format Feedback (JS, 6 строк) → tg_copy.
# Telegram-нода n8n теперь подтягивает текст через /tg/copy/{key}.
FEEDBACK_DEFAULT_TEXT = "Оценка принята."
FEEDBACK_HUMAN_TEXT = (
    "Ваш запрос направлен HR/Legal на ручную обработку. Ответ придёт от профильного "
    "специалиста — сроки зависят от очереди ревью."
)


COPY_BLOCKS: dict[str, str] = {
    "greeting": GREETING_TEXT,
    "help": HELP_TEXT,
    "clear": CLEAR_TEXT,
    "empty_input": EMPTY_INPUT_TEXT,
    "thanks": THANKS_TEXT,
    "unknown_feedback_reason": UNKNOWN_FEEDBACK_REASON_TEXT,
    "unknown_feedback": UNKNOWN_FEEDBACK_TEXT,
    "unrecognized_followup": UNRECOGNIZED_FOLLOWUP_TEXT,
    "feedback_default": FEEDBACK_DEFAULT_TEXT,
    "feedback_human": FEEDBACK_HUMAN_TEXT,
}
