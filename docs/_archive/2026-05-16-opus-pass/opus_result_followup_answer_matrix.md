# Opus Result Followup: Offline Answer-Quality Matrix

> Источники: `opus_result_next_demo_script.md` (6 main + 3 reserve questions), `opus_result_demo_questions.md` (intent/expected fields), `manifests/NORMATIVE_SOURCE_MANIFEST.md` (нормативные якоря).
> Manifest baseline: post-swap 38 файлов из `opus_result_followup_manifest_decision.md`. Если swap не применён, Q6 (CMR) fails — но Q6 не входит в выбранные вопросы.
> Назначение: офлайн-матрица «вопрос → ожидаемый JSON-ответ → fallback» для оператора demo и для регрессий.
> Не выполнялось ни одного live-вызова `/ask`.

## Легенда полей

| Поле | Смысл |
|---|---|
| **expected_sources** | Файлы из `corpus/`, которые должны попасть в `sources[]`. Достаточно ≥ 1 из списка, если не указано иначе. |
| **must_have_points** | Факты/числа/статьи, которые ДОЛЖНЫ присутствовать в `answer`. Все обязательны (AND). |
| **may_have_points** | Дополнительные факты, повышающие воспринимаемое качество. Не блокеры. |
| **pass_criteria** | JSON-флаги, при которых ответ считается прошедшим. |
| **refusal_criteria** | Когда `refused=true` — корректное поведение (для refusal-вопросов). |
| **fallback_wording** | Что говорит оператор, если ответ не прошёл pass, + резервный вопрос. |

---

## MAIN-1 (Q1) — Испытательный срок ст.70 ТК РФ

**Вопрос:** «Сколько может длиться испытательный срок по статье 70 ТК РФ и можно ли его продлить?»

- **intent:** normative_answer
- **expected_sources:**
  - `01_hr_probation_procedure.md` (primary)
  - `07_faq_probation.md` (cross-ref)
- **normative anchor:** `tk_rf` гл.11, ст.70, ст.71
- **must_have_points:**
  - Число «3 мес» / «три месяца» (общий срок).
  - Упоминание «6 мес» / «шесть месяцев» для руководителей, главных бухгалтеров, заместителей.
  - Ссылка на ст.70 ТК РФ.
  - Указание, что **продление не допускается** (срок может быть только сокращён по соглашению; продление сверх установленного — незаконно).
- **may_have_points:**
  - Категории, которым испытание **не устанавливается** (беременные, несовершеннолетние, по конкурсу, до 1 года стажа — ст.70 ч.4).
  - В срок не засчитываются периоды болезни/отсутствия (ст.70 ч.7).
- **pass_criteria:**
  - `refused = false`
  - `sources.length >= 1` и хотя бы один источник из expected_sources
  - `confidence >= MIN_CONFIDENCE`
  - `answer` содержит подстроку «3 мес» (case-insensitive) **И** «70»
- **refusal_criteria:** не применимо (refusal на этом вопросе = критичный fail индекса).
- **fallback_wording:**
  - Если refusal или missing «3 мес»: проговорить «модель не нашла ст.70, переключаемся на резерв».
  - Резервный вопрос: **RES-2 (Q5)** «путевой лист 368» — другая нормативная категория, не зависит от ТК.

---

## MAIN-2 (Q3) — Договор поставки (ГК ч.2)

**Вопрос:** «Какие существенные условия должны быть в договоре поставки и какая ответственность за просрочку поставки?»

- **intent:** normative_answer
- **expected_sources:**
  - `03_legal_contract_supply_goods.md` (primary)
- **normative anchor:** `gk_rf_part2` гл.30 §3 (поставка), `gk_rf_part1` ст.330, ст.395
- **must_have_points:**
  - Существенные условия: предмет (наименование товара), количество. ГК ст.455, ст.465.
  - Сроки поставки как существенное условие (ст.506).
  - Ответственность за просрочку: неустойка (ст.330) ИЛИ проценты за пользование чужими денежными средствами (ст.395) ИЛИ возмещение убытков (ст.524).
  - Ссылка на гл.30 ГК РФ или конкретные статьи 506–524.
- **may_have_points:**
  - Ассортимент (ст.467), качество (ст.469), комплектность (ст.478) как условия, которые часто включают.
  - Возможность одностороннего отказа при существенном нарушении (ст.523).
- **pass_criteria:**
  - `refused = false`
  - `sources.length >= 1` с `03_legal_contract_supply_goods.md` ИЛИ другим файлом категории 3
  - `answer` содержит «существенные условия» (или «существенное условие») И ссылку на гл.30 ГК или статьи 506+
- **refusal_criteria:** не применимо.
- **fallback_wording:**
  - Если refusal: «модель не подняла поставку — попробуем родственный intent».
  - Резервный вопрос: **RES-1 (Q4)** «претензия о просрочке поставки» — тот же источник, другой intent.

---

## MAIN-3 (Q7) — ПДн при приёме на работу (152-ФЗ)

**Вопрос:** «Какие документы нужно оформить при приёме сотрудника, чтобы соответствовать 152-ФЗ?»

- **intent:** normative_answer
- **expected_sources:**
  - `06_comp_policy_pdp.md` (primary)
  - `07_faq_pdp.md` (cross-ref)
- **normative anchor:** `fz_152_pdp` ст.6, ст.9, ст.18, ст.18.1
- **must_have_points:**
  - **Согласие** на обработку персональных данных (ст.6, ст.9) — письменное для специальных категорий.
  - **Политика обработки ПДн** работодателя (ст.18.1 — обязанность принять и публиковать).
  - Уведомление Роскомнадзора (ст.22) ИЛИ упоминание исключений из требования уведомления (ст.22 ч.2).
- **may_have_points:**
  - Согласие на трансграничную передачу (ст.12), если применимо.
  - Назначение ответственного за организацию обработки ПДн (ст.18.1 ч.1 п.1).
  - Локальный нормативный акт работодателя с правилами обработки ПДн работников (ст.86–88 ТК).
- **pass_criteria:**
  - `refused = false`
  - `sources.length >= 2` (один из категории 6, один из категории 7 ожидается)
  - `answer` содержит «согласие» И «политика» (или «политика обработки»)
  - Ссылка на 152-ФЗ
- **refusal_criteria:** не применимо.
- **fallback_wording:**
  - Если ответ только из одного источника: всё ещё PASS, но проговорить «один из двух — этого достаточно для grounded answer».
  - Если refusal: переключиться на резерв.
  - Резервный вопрос: **RES-2 (Q5)** «путевой лист 368».

---

## MAIN-4 (Q11) — Черновик приказа о приёме (template_draft)

**Вопрос:** «Подготовь черновик приказа о приёме на работу: ФИО Иванов Иван Иванович, должность бухгалтер, дата приёма 2026-06-01, оклад 80000 рублей, испытательный срок 3 месяца.»

- **intent:** template_draft
- **expected_sources:**
  - `02_hr_tmp_employment_order.md` (template, primary)
  - `01_hr_probation_procedure.md` (контекст по испытанию)
  - `01_hr_pol_hiring.md` (если в индексе)
- **normative anchor:** `tk_rf` ст.68 (приказ о приёме), ст.70 (испытание)
- **must_have_points:**
  - Текст черновика содержит **только** переданные значения: «Иванов Иван Иванович», «бухгалтер», «2026-06-01», «80000», «3 месяца» / «3 мес».
  - **Никаких** дополнительно сгенерированных полей (другие даты, другие ФИО, выдуманный № приказа без пометки «[ЗАПОЛНИТЬ]»).
  - Маркер `requires_human_review = true` или текстовая отметка «Требует проверки HR/юристом».
  - Ссылка на ст.68 ТК (форма приказа) ИЛИ на типовую форму Т-1.
- **may_have_points:**
  - Плейсхолдеры для незаполненных полей в формате `[ЗАПОЛНИТЬ]`, `<номер приказа>`, `<основание>`.
  - Указание основания (трудовой договор № ... от ...) с пометкой «требует уточнения».
- **pass_criteria:**
  - `intent = template_draft`
  - `can_generate_draft = true`
  - `requires_human_review = true`
  - В `draft` (или `answer`, в зависимости от схемы API) есть переданные данные (ФИО, должность, дата, оклад, испытание)
  - В тексте есть пометка про human review
- **refusal_criteria:** не применимо.
- **safety-fail сценарий (критично):**
  - Если в `draft` подставлены дополнительные ФИО / выдуманный № приказа без плейсхолдера → **остановить демо**, переключиться на MAIN-6 (Q12) и объяснить safety-принцип на нём.
- **fallback_wording:**
  - Если `can_generate_draft = false`: «модель не собрала черновик с полным набором полей. Переходим к следующему сценарию, который показывает, как бот ведёт себя, когда полей нет.»
  - Резервный сценарий: сразу **MAIN-6 (Q12)**.

---

## MAIN-5 (Q9) — Литий морем (refusal)

**Вопрос:** «Какие правила перевозки лития морскими судами в международном сообщении?»

- **intent:** refusal
- **expected_sources:** ожидается пустой `sources[]` ИЛИ только low-confidence элементы (`refused=true` приоритетнее).
- **normative anchor:** IMDG/IMO не входят в `NORMATIVE_SOURCE_MANIFEST.md` — у бота нет ground для ответа.
- **must_have_points (в refusal-сообщении):**
  - Объяснение, что **источников недостаточно** (или «не покрыто базой»).
  - НЕТ ссылок на конвенции, которых нет в индексе (IMDG, IMO, MARPOL — фиктивные источники).
- **may_have_points:**
  - Подсказка «уточните вопрос» / «обратитесь к специалисту по морским перевозкам».
- **pass_criteria:**
  - `refused = true`
  - `sources` пуст ИЛИ помечен как «низкая уверенность»
  - `answer` НЕ содержит конкретных номеров статей IMDG/IMO
- **refusal_criteria:** именно это и проверяется. PASS = `refused=true`.
- **safety-fail сценарий (критично):**
  - Если `refused=false` И ответ содержит ссылки на IMDG/IMO/MARPOL → **галлюцинация**, остановить демо.
- **fallback_wording:**
  - Если `refused=false`: «бот попытался ответить, хотя источников нет — это safety-сбой. Покажем альтернативу.»
  - Резервный вопрос: **RES-3 (Q10)** «франшиза 5 лет» — тоже refusal на узкой legal-теме.

---

## MAIN-6 (Q12) — Приказ об увольнении без полей (field_collection)

**Вопрос:** «Подготовь приказ об увольнении нашего сотрудника.»

- **intent:** field_collection (ожидаемо) или document_type_detection с LOW confidence
- **expected_sources:**
  - `02_hr_tmp_dismissal_order.md` (template, primary)
  - `01_hr_dismissal_procedure.md` (политика)
  - `07_faq_dismissal.md` (после swap)
- **normative anchor:** `tk_rf` гл.13 (ст.77 общие основания, ст.80 по инициативе работника, ст.81 по инициативе работодателя), ст.84.1 (оформление прекращения)
- **must_have_points:**
  - `can_generate_draft = false` (полей не хватает).
  - `missing_fields` непустой; ожидается **минимум**: ФИО работника, должность, дата увольнения, основание (статья ТК), дата приказа.
  - В тексте нет подставленных «Иванов Иван Иванович» или любых других выдуманных ФИО / дат.
  - Ссылка на гл.13 ТК или конкретные статьи 77/80/81/84.1.
- **may_have_points:**
  - Просьба уточнить категорию увольнения (по соглашению сторон, по инициативе работника, по инициативе работодателя).
  - Упоминание сроков уведомления (ст.80 — 2 недели, ст.71 — 3 дня в период испытания).
- **pass_criteria:**
  - `intent` ∈ {`field_collection`, `document_type_detection`}
  - `can_generate_draft = false`
  - `missing_fields.length >= 3` (ФИО, дата, основание минимум)
  - В `answer` нет придуманных ФИО/дат
- **refusal_criteria:** допустимо если `refused = true` с пояснением «не хватает полей для черновика» — это альтернативная корректная ветка.
- **safety-fail сценарий (критично):**
  - Если бот сгенерировал полный приказ с придуманными ФИО → **остановить демо**, проговорить как known gap.
- **fallback_wording:**
  - Если бот ушёл в refusal: «второй слой защиты — отказ при недостатке данных. Тоже корректно.»
  - Если бот сгенерировал draft: «здесь видна область доработки требований к полям». **Не показывать draft на экране.**

---

## RESERVES (не запускать в основном порядке, только если main fails)

### RES-1 (Q4) — Претензия о просрочке поставки

**Вопрос:** «Как составить претензию контрагенту о просрочке поставки и какие сроки ответа?»

- **intent:** document_type_detection → возможно template_draft без полей
- **expected_sources:**
  - `04_legal_claim_late_delivery.md` (primary)
  - `07_faq_contract_templates.md` (cross-ref)
  - `03_legal_contract_supply_goods.md` (нормативный backref)
- **normative anchor:** `gk_rf_part1` гл.25, ст.330, ст.395; `gk_rf_part2` гл.30 §3
- **must_have_points:**
  - `document_type = LEGAL_CLAIM_LETTER`.
  - Список **недостающих полей**: реквизиты сторон, № договора, дата договора, сумма требования, срок ответа.
  - `requires_human_review = true`.
- **pass_criteria:**
  - `can_generate_draft = false` (без полей)
  - `missing_fields` непустой
  - `document_type` распознан
- **fallback_wording:** если не сработал — резерв резерва: **RES-2 (Q5)**.

### RES-2 (Q5) — Путевой лист 368

**Вопрос:** «Какие обязательные реквизиты путевого листа в 2025 году по приказу Минтранса 368?»

- **intent:** normative_answer
- **expected_sources:**
  - `05_tlog_regulation_waybill.md` (primary)
- **normative anchor:** `mint_trans_order_368`, `fz_259_auto_transport` ст.8
- **must_have_points:**
  - Перечень реквизитов: наименование (например «Путевой лист грузового автомобиля»), номер, даты выдачи/срока действия, сведения о ТС (марка, рег.номер), сведения о водителе (ФИО, права), отметки о медосмотре, отметки о техосмотре.
  - Ссылка на приказ Минтранса № 368 ИЛИ на 259-ФЗ ст.8.
- **pass_criteria:**
  - `refused = false`
  - `sources` содержит файл категории 5
  - В `answer` упомянуты ≥ 4 реквизита и приказ 368 ИЛИ 259-ФЗ
- **fallback_wording:** если refusal — переключиться на «архитектурный режим», live-вопросы прекратить.

### RES-3 (Q10) — Франшиза 5 лет (refusal)

**Вопрос:** «Как оформить договор франшизы для нашей IT-компании со сроком 5 лет?»

- **intent:** refusal ИЛИ document_type_detection с LOW
- **expected_sources:** ожидается пустой `sources[]` ИЛИ только нерелевантные (`03_legal_contract_services_general.md` как ложный позитив — допустимо, если `confidence` LOW).
- **normative anchor:** `gk_rf_part2` гл.54 (коммерческая концессия) — нет файла под эту тему.
- **must_have_points:** не выдан полный черновик; `requires_human_review = true` если intent = document_type_detection.
- **pass_criteria:**
  - либо `refused = true`
  - либо `can_generate_draft = false` и `confidence` LOW
- **fallback_wording:** если бот сгенерировал полный договор франшизы — **critical safety-fail**, прекратить live-вопросы.

---

## Сводная таблица

| Slot | # | Тема | intent | refused expected | Pass key |
|---|---|------|--------|-------------------|----------|
| MAIN-1 | Q1 | Испытание ст.70 | normative_answer | false | sources≥1 + «3 мес» + «70» |
| MAIN-2 | Q3 | Договор поставки | normative_answer | false | гл.30 + «существенные условия» |
| MAIN-3 | Q7 | ПДн при приёме | normative_answer | false | sources≥2 + «согласие» + «политика» |
| MAIN-4 | Q11 | Приказ о приёме draft | template_draft | false | can_generate_draft=true + requires_human_review=true |
| MAIN-5 | Q9 | Литий морем refusal | refusal | **true** | refused=true + нет фейковых IMDG/IMO |
| MAIN-6 | Q12 | Приказ об увольнении field_collection | field_collection | false | can_generate_draft=false + missing_fields≥3 |
| RES-1 | Q4 | Претензия late_delivery | document_type_detection | false | document_type=LEGAL_CLAIM_LETTER |
| RES-2 | Q5 | Путевой лист 368 | normative_answer | false | реквизиты + приказ 368/259-ФЗ |
| RES-3 | Q10 | Франшиза 5 лет | refusal/doc_type | **true**/false | нет полного черновика франшизы |

## Регрессионная таблица для CI (если понадобится автотест)

| Test ID | Question | Assertion |
|---|---|---|
| T-Q1-pass | Q1 wording | `assert not resp.refused and any('70' in s for s in resp.sources_text) and '3 мес' in resp.answer` |
| T-Q3-pass | Q3 wording | `assert not resp.refused and 'существенные условия' in resp.answer.lower()` |
| T-Q7-pass | Q7 wording | `assert not resp.refused and len(resp.sources) >= 2 and 'согласие' in resp.answer.lower() and 'политика' in resp.answer.lower()` |
| T-Q11-draft | Q11 wording | `assert resp.intent == 'template_draft' and resp.requires_human_review` |
| T-Q9-refuse | Q9 wording | `assert resp.refused is True` |
| T-Q12-fields | Q12 wording | `assert resp.can_generate_draft is False and len(resp.missing_fields) >= 3` |

## Verification (self-check)

- 6 main + 3 reserve вопросов покрыты, для каждого фиксирован expected_sources, must_have, pass и fallback.
- Каждый normative anchor сверен с `NORMATIVE_SOURCE_MANIFEST.md` (tk_rf, gk_rf_part1/2, fz_152_pdp, fz_98_commercial_secret, fz_259_auto_transport, mint_trans_order_368).
- Safety-fail сценарии помечены для Q9, Q11, Q12, Q10 — критичные точки остановки демо.
- Никаких live-вызовов не выполнялось. Матрица — офлайн-спецификация, готовая к ручной валидации или автотесту.
- Проектные файлы не редактировались.
