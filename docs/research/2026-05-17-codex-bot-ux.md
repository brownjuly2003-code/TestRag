# Codex Research: HR/Legal RAG Telegram-bot UX (2026-05-17)

Запрошено через codex-companion / codex:rescue. Тот же промпт, что у Kimi (`2026-05-17-kimi-bot-ux.md`).

---

## MUST-HAVE for shippable MVP

### 1. Feedback — двухшаговый для негатива

Оставь `Полезно / Неточно / Нужны источники`, но при нажатии «Неточно» показывай категории: `не тот документ / устаревший документ / ошибка в фактах / неполный ответ / нужен человек`, потом опциональный free-text. Именно так работают: Microsoft Copilot (rating + optional comments + diagnostics), AWS Kendra (feedback привязан к `QueryId` + `ResultId` = конкретный chunk), LangSmith (feedback на traces и child runs). Один thumbs-down без категории — слишком грубо для retrieval-дебаггинга.

### 2. Citations по умолчанию, не по кнопке

2-4 источника в конце каждого ответа `[1][2]` — обязательно для HR/legal. Прятать за кнопку «Нужны источники» — антипаттерн: пользователь обязан видеть источник без доп. клика. Notion AI, Copilot, Glean, Kendra — все показывают grounding source inline. В авиа-груз HR/legal всегда указывай: название документа, дату/версию политики.

### 3. Telegram-польшир минимальный сет

- `typing` action сразу при получении запроса, до retrieval — иначе бот кажется зависшим
- `/help`, `/clear`, `/history` (последние 5-10 запросов) — обязательны
- Markdown: **жирный** для ключевых выводов, `code` для номеров статей/пунктов, списки для условий. Telegram parse_mode=HTML или MarkdownV2
- Ответ: 700-1200 символов основной текст + «Источники» блок. Длиннее — collapse или кнопка «Развернуть»
- Disclaimer в конце: «Ответ носит справочный характер. Уточняйте у HR/юриста.» — одна строка, не перед ответом

### 4. Confidence — поведенческий, не числовой

Вместо «уверенность 73%» (fake precision): «Найдено 3 документа по теме; если ситуация нестандартная — уточни детали». При < 1 релевантного chunk: «Точного ответа в документах компании не нашла. Свяжись с HR напрямую.»

### 5. Observability (внутренняя, не UX)

Логируй: query, retrieved doc IDs + chunk IDs, citation set, feedback category, source-clicks, latency до первого токена, latency полная, follow-up через < 60с. Без этого feedback бесполезен.

---

## NICE-TO-HAVE

- Follow-up кнопки после ответа: `Уточнить`, `Развернуть`, `Создать задачу HR` — полезны, вторичны
- Human handoff при низкой уверенности или категории `нужен человек`
- `/docs` — список доступных разделов корпуса
- История как `/history` с последними 5 вопросами

---

## ANTI-PATTERNS — убери из плана

- Confidence % как число — false precision, вводит в заблуждение
- Полный preview документа внутри чата
- Длинный юридический дисклеймер ДО ответа
- Обязательный free-text feedback после каждого ответа
- Sources только по кнопке (убери текущую кнопку «Нужны источники», замени на always-on citations)
- Nested меню с 3+ уровнями

---

## Ссылки

- AWS Kendra feedback API: https://docs.aws.amazon.com/kendra/latest/dg/submitting-feedback.html
- LangSmith tracing + feedback: https://docs.smith.langchain.com
- Microsoft Copilot feedback: https://support.microsoft.com/en-us/topic/providing-feedback-about-microsoft-copilot-with-microsoft-365-apps
- Anthropic Claude for Work feedback settings: https://support.anthropic.com/en/articles/10504844
- Intercom Fin reporting: https://intercom.com/help
- Ada AI reporting: https://docs.ada.cx
- Glean Assistant docs: https://docs.glean.com
- Telegram Bot API: https://core.telegram.org/bots/api
