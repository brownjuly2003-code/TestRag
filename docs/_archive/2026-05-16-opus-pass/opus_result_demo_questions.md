# Opus Result: Demo Question Set

> Источник: `manifests/MANIFEST.md`, `manifests/NORMATIVE_SOURCE_MANIFEST.md`, `docs/demo-runbook.md`, `docs/legal-document-prompts.md`, корпус-shortlist из `opus_result_corpus.md`.
> Назначение: 12 demo-вопросов для прогонки end-to-end (Telegram → n8n → RAG API → ответ + feedback).
> Структура каждого вопроса: текст → ожидаемое поведение API → expected sources → проверочный критерий.

## Легенда

- **intent**: соответствует enum из `docs/legal-document-prompts.md` (normative_answer / document_type_detection / template_draft / field_collection / refusal).
- **confidence**: HIGH / MEDIUM / LOW по тому же документу.
- **refused**: ожидаемый флаг в ответе RAG API.
- **source category**: категория из `manifests/MANIFEST.md` (1–7) и `source_id` из `NORMATIVE_SOURCE_MANIFEST.md`.

---

## 1. HR — нормативный вопрос (happy path)

**Вопрос:** «Сколько может длиться испытательный срок по статье 70 ТК РФ и можно ли его продлить?»

- **intent:** normative_answer
- **confidence:** HIGH
- **refused:** false
- **source category:** Кат.1 (HR policies) + Кат.7 (FAQ). Файлы: `01_hr_probation_procedure.md`, `07_faq_probation.md` (если включён). normative: `tk_rf` (гл.11).
- **expected behaviour:** ответ цитирует ст.70, max срок 3 мес (для руководителей до 6 мес), показывает 1–2 источника со ссылкой на ТК РФ.
- **pass/fail:** `sources` ≥ 1, упомянут хотя бы один файл из shortlist, нет фразы «не нашёл», `confidence ≥ MIN_CONFIDENCE`.

## 2. HR — отпуска (ground для template_draft)

**Вопрос:** «Какова минимальная продолжительность ежегодного оплачиваемого отпуска и как считать дни при работе на 0.5 ставки?»

- **intent:** normative_answer
- **confidence:** HIGH
- **source category:** Кат.1 (`01_hr_pol_leave.md`, `01_hr_pol_part_time.md`) + Кат.7 (`07_faq_leave.md`). normative: `tk_rf` гл.19.
- **expected behaviour:** 28 календ. дней, ст.115 ТК; неполное время не урезает отпуск (ст.93 ТК).
- **pass/fail:** ответ содержит число «28», ссылка на гл.19/ст.115; не подставляет конкретные расчёты по фейковой ставке.

## 3. Legal — договор поставки (ГК ч.2)

**Вопрос:** «Какие существенные условия должны быть в договоре поставки и какая ответственность за просрочку поставки?»

- **intent:** normative_answer
- **confidence:** HIGH
- **source category:** Кат.3 (`03_legal_contract_supply_goods.md`). normative: `gk_rf_part2` (гл.30), `gk_rf_part1` ст.330-333.
- **expected behaviour:** предмет, количество, ассортимент, сроки; неустойка (ГК ст.330) или проценты (ст.395) — ссылки в `sources`.
- **pass/fail:** упоминание «существенные условия» + статьи из гл.30; источник из корпуса категории 3.

## 4. Legal — претензионная работа

**Вопрос:** «Как составить претензию контрагенту о просрочке поставки и какие сроки ответа?»

- **intent:** document_type_detection → template_draft
- **confidence:** MEDIUM (нет реквизитов сторон)
- **source category:** Кат.4 (`04_legal_claim_late_delivery.md`), Кат.7 (`07_faq_claims_procedure.md`). normative: `gk_rf_part1` гл.25, `gk_rf_part2` гл.30.
- **expected behaviour:** API возвращает intent=`document_type_detection`, document_type=`LEGAL_CLAIM_LETTER`, requires_human_review=true, перечислены недостающие поля: «реквизиты сторон, номер договора, сумма, срок ответа».
- **pass/fail:** в JSON ответе `can_generate_draft=false` (нет полей), `missing_fields` непустой.

## 5. Logistics — путевой лист (узкий нормативный)

**Вопрос:** «Какие обязательные реквизиты путевого листа в 2025 году по приказу Минтранса 368?»

- **intent:** normative_answer
- **confidence:** HIGH
- **source category:** Кат.5 (`05_tlog_regulation_waybill.md`). normative: `mint_trans_order_368`, `fz_259_auto_transport` ст.8.
- **expected behaviour:** перечислены реквизиты (наименование, номер, даты, сведения о ТС, водителе, отметки о медосмотре).
- **pass/fail:** ссылка на приказ №368 или 259-ФЗ ст.8; источник из категории 5.

## 6. Logistics — международная перевозка (CMR)

**Вопрос:** «В какой срок нужно подать претензию международному автоперевозчику по конвенции CMR?»

- **intent:** normative_answer
- **confidence:** MEDIUM (CMR — secondary source)
- **source category:** Кат.5 (`05_tlog_regulation_cmr.md`). normative: `cmr_convention` (Глава IV).
- **expected behaviour:** ответ упоминает 7 дней (явная утрата при приёмке) / 21 день (просрочка) / 1 год (исковая давность) — по тексту CMR; добавляет дисклеймер «уточнить редакцию».
- **pass/fail:** упомянут CMR; ответ не подменяет CMR Уставом автомобильного транспорта.

## 7. Compliance — персональные данные

**Вопрос:** «Какие документы нужно оформить при приёме сотрудника, чтобы соответствовать 152-ФЗ?»

- **intent:** normative_answer
- **confidence:** HIGH
- **source category:** Кат.6 (`06_comp_policy_pdp.md`, `06_comp_policy_consent_form.md`), Кат.7 (`07_faq_pdp.md`). normative: `fz_152_pdp` ст.6, 9, 18.
- **expected behaviour:** согласие на ОПДн, политика обработки ПДн (ст.18.1), уведомление Роскомнадзора; ссылки на 152-ФЗ.
- **pass/fail:** ответ содержит «согласие» + «политика»; ≥ 2 источника (один внутренний, один нормативный).

## 8. Compliance — коммерческая тайна

**Вопрос:** «Какие сведения можно отнести к коммерческой тайне и что включить в NDA с сотрудником?»

- **intent:** normative_answer
- **confidence:** HIGH
- **source category:** Кат.6 (`06_comp_policy_commercial_secret.md`, `06_comp_policy_nda_employee.md`). normative: `fz_98_commercial_secret` ст.3, 6.
- **expected behaviour:** перечень исключений (ст.5), требования режима (ст.10 — гриф, учёт, ознакомление работника), типовые пункты NDA.
- **pass/fail:** упомянуто 98-ФЗ и ст.3/6; sources ≥ 2.

## 9. Low-confidence refusal — out-of-scope (морские перевозки)

**Вопрос:** «Какие правила перевозки лития морскими судами в международном сообщении?»

- **intent:** refusal
- **confidence:** LOW
- **refused:** true
- **source category:** НЕ покрыто shortlist (`05_tlog_contract_transport_sea.md` исключён). normative: нет соответствующего source_id (IMO/IMDG не в normative manifest).
- **expected behaviour:** `refused=true`, текст «недостаточно источников / уточните вопрос», нет выдуманных норм.
- **pass/fail:** `refused=true`; в логе `request_logs.status='refused'`; ответ не содержит фейковых ссылок на конвенции.

## 10. Low-confidence refusal — узкая юридическая тема

**Вопрос:** «Как оформить договор франшизы для нашей IT-компании со сроком 5 лет?»

- **intent:** refusal или document_type_detection с LOW
- **confidence:** LOW
- **refused:** true (`03_legal_contract_franchise.md` исключён из shortlist)
- **source category:** normative: `gk_rf_part2` глава 54 (коммерческая концессия) — в shortlist нет файла под эту тему.
- **expected behaviour:** API возвращает либо `refused=true`, либо `intent=document_type_detection` с `confidence=LOW` и списком недостающих документов.
- **pass/fail:** не выдан полный черновик; `requires_human_review=true`; sources либо пустые, либо помечены как недостаточные.

## 11. Template draft — happy path (приказ о приёме)

**Вопрос:** «Подготовь черновик приказа о приёме на работу: ФИО Иванов Иван Иванович, должность бухгалтер, дата приёма 2026-06-01, оклад 80000 рублей, испытательный срок 3 месяца.»

- **intent:** template_draft
- **confidence:** HIGH (все обязательные поля переданы)
- **source category:** Кат.2 (`02_hr_tmp_employment_order.md`), Кат.1 (`01_hr_pol_hiring.md`, `01_hr_probation_procedure.md`). normative: `tk_rf` ст.68, 70.
- **expected behaviour:** JSON ответ с `document_type=HR_ORDER_HIRING`, `can_generate_draft=true`, `requires_human_review=true`, в `draft` — поля шаблона заполнены через код, явный маркер «Требует проверки HR/юристом».
- **pass/fail:** в ответе есть `draft` (или поле эквивалента), оклад/имя не «дофантазированы» (только переданные), ссылка на ст.68/70.

## 12. Template draft — field_collection (недостающие поля)

**Вопрос:** «Подготовь приказ об увольнении нашего сотрудника.»

- **intent:** field_collection
- **confidence:** MEDIUM
- **source category:** Кат.2 (`02_hr_tmp_dismissal_order.md`), Кат.1 (`01_hr_dismissal_procedure.md`). normative: `tk_rf` гл.13 (ст.77, 80, 81).
- **expected behaviour:** API возвращает `intent=field_collection`, `can_generate_draft=false`, список недостающих полей: ФИО, должность, дата увольнения, основание (ст.77/80/81), дата приказа.
- **pass/fail:** `missing_fields` непустой; LLM не подставляет ФИО/основание сама; ссылка на гл.13 ТК.

---

## Сводная таблица для оператора demo

| # | Тема | intent | refused | confidence | критерий «pass» |
|---|------|--------|---------|------------|-----------------|
| 1 | Испытание ст.70 | normative_answer | false | HIGH | sources ≥ 1, ст.70 |
| 2 | Отпуск 28 дней | normative_answer | false | HIGH | число 28, гл.19 |
| 3 | Договор поставки | normative_answer | false | HIGH | гл.30 ГК ч.2 |
| 4 | Претензия | document_type_detection | false | MEDIUM | LEGAL_CLAIM_LETTER + missing_fields |
| 5 | Путевой лист | normative_answer | false | HIGH | приказ 368 / 259-ФЗ ст.8 |
| 6 | CMR претензия | normative_answer | false | MEDIUM | сроки 7/21/365 дней |
| 7 | ПДн при приёме | normative_answer | false | HIGH | 152-ФЗ + sources ≥ 2 |
| 8 | Коммерческая тайна | normative_answer | false | HIGH | 98-ФЗ ст.3, ст.6 |
| 9 | Литий морем | refusal | **true** | LOW | refused=true, нет фейка |
| 10 | Франшиза 5 лет | refusal / draft | **true/MEDIUM** | LOW | нет полного черновика |
| 11 | Приказ о приёме | template_draft | false | HIGH | draft + requires_human_review |
| 12 | Приказ об увольнении | field_collection | false | MEDIUM | missing_fields непустой |

## Покрытие интентов

- normative_answer: 1, 2, 3, 5, 6, 7, 8 (7/12)
- document_type_detection: 4 (1/12)
- template_draft: 11 (1/12)
- field_collection: 12 (1/12)
- refusal: 9, 10 (2/12)

Соответствие enum из `legal-document-prompts.md` — полное.

## Покрытие категорий MANIFEST

- Кат.1 (HR policies): 1, 2, 7, 11, 12
- Кат.2 (HR templates): 11, 12
- Кат.3 (Legal contracts): 3, 10
- Кат.4 (Claims): 4
- Кат.5 (Transport/logistics): 5, 6, 9
- Кат.6 (Compliance): 7, 8
- Кат.7 (FAQ): 1, 2, 7 (cross-ref)

Все 7 категорий MANIFEST затрагиваются хотя бы одним вопросом.

## Не покрыто намеренно

- Внутренние юридические справки (`04_legal_memo_*`) — нет в demo-runbook как сценарий.
- Должностные инструкции — не входят в публичный демо-поток.
- Антикоррупция/конфликт интересов — оставить как «второй раунд» вопросов.
