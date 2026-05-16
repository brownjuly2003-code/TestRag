# Opus Result Next: Manifest Delta

> Source A: `manifests/MVP_CORPUS_FILES.txt` (current ingestion manifest, 38 файлов после комментариев).
> Source B: `opus_result_corpus.md` §Shortlist (30 файлов, аудитированный baseline для MVP).
> Назначение: показать, что реально проиндексируется на ingestion, и где это разойдётся с demo-вопросами.
> Никаких правок в `manifests/`, `corpus/`, `rag-api/` не делалось.

## Сводка

- MVP_CORPUS_FILES.txt = 38 файлов.
- Shortlist = 30 файлов.
- Пересечение = 24 файла.
- В current нет 6 файлов из shortlist (removals → нужно добавить).
- В current 14 файлов вне shortlist (additions → можно держать или сократить).
- Net дельта на demo-вопросы: критично страдает только Q6 (CMR), частично Q2 (leave FAQ) и Q8 (NDA employee).

## Файлы, которые есть в shortlist, но НЕТ в текущем MVP_CORPUS_FILES.txt

| # | Файл | Категория | Зачем нужен | Impact на demo |
|---|------|-----------|-------------|----------------|
| R1 | `01_hr_pol_maternity.md` | 1 | Декрет / 255-ФЗ (high priority в MANIFEST) | Не блокирует 12 demo-вопросов, но усиливает HR-кейс |
| R2 | `01_hr_pol_injury.md` | 1 | 125-ФЗ соцстрахование | Не в demo-вопросах |
| R3 | `05_tlog_regulation_cmr.md` | 5 | CMR-конвенция, международные перевозки | **Блокирует Q6 (CMR претензия)** — без файла ответ уйдёт в refusal |
| R4 | `06_comp_policy_nda_employee.md` | 6 | NDA сотрудника, intent LEGAL_NDA | **Ослабляет Q8** (commercial secret + NDA) — commercial_secret покрывает только половину |
| R5 | `07_faq_leave.md` | 7 | Cross-ref для отпуск | Снижает confidence Q2 (28 дней), но не блокирует |
| R6 | `07_faq_dismissal.md` | 7 | Cross-ref для увольнения | Не блокирует Q12 (там работает 02_hr_tmp_dismissal_order + 01_hr_dismissal_procedure) |

**Критические для demo:** R3 (CMR), R4 (NDA).

## Файлы, которые есть в текущем MVP_CORPUS_FILES.txt, но НЕТ в shortlist

| # | Файл | Категория | Почему не в shortlist | Держать/убрать |
|---|------|-----------|------------------------|-----------------|
| A1 | `01_hr_pol_harassment.md` | 1 | Не в hot path demo, нет нормативного якоря | Держать, low cost |
| A2 | `01_hr_pol_confidentiality_emp.md` | 1 | Дубль с 06_comp_policy_commercial_secret | Держать (парный, polish) |
| A3 | `01_hr_pol_corruption.md` | 1 | Антикоррупция — «второй раунд» | Держать |
| A4 | `02_hr_tmp_remote_work_agreement.md` | 2 | Был open question #1 в `opus_result_corpus.md` | Держать — нужен для intent HR_ADDITIONAL_AGREEMENT remote |
| A5 | `03_legal_contract_ndc.md` | 3 | NDA контрагент, не в shortlist | Держать (полезен с A2) |
| A6 | `03_legal_contract_customs_broker.md` | 3 | Узкая ниша | **Можно убрать** для бюджета |
| A7 | `03_legal_contract_termination_checklist.md` | 3 | Operational checklist, не нормативный | **Можно убрать** |
| A8 | `04_legal_claim_defective_goods.md` | 4 | Дубль с late_delivery по схеме претензии | Держать (расширяет Q4) |
| A9 | `04_legal_claim_non_payment.md` | 4 | Дубль с late_delivery | **Можно убрать** |
| A10 | `05_tlog_contract_transport_road.md` | 5 | Дубль с 03_legal_contract_cargo_transport_road | Держать (operational pair) |
| A11 | `05_tlog_regulation_customs_clearance.md` | 5 | Узкая ниша | **Можно убрать** |
| A12 | `06_comp_policy_incident_response.md` | 6 | Не в demo-вопросах | Держать (один кейс безопасности — полезно) |
| A13 | `07_faq_probation.md` | 7 | Заменяет faq_leave/faq_dismissal в shortlist | **Держать**, усиливает Q1 |
| A14 | `07_faq_contract_templates.md` | 7 | Cross-ref для шаблонов | Держать |

## Impact на 12 demo-вопросов из `opus_result_demo_questions.md`

| # | Тема | Покрытие в current manifest | Статус |
|---|------|------------------------------|--------|
| 1 | Испытание ст.70 ТК | `01_hr_probation_procedure.md` + `07_faq_probation.md` | ✅ PASS — даже лучше shortlist (FAQ в индексе) |
| 2 | Отпуск 28 дней | `01_hr_pol_leave.md` (faq_leave отсутствует) | ⚠️ PASS, но ниже confidence без FAQ-rerank |
| 3 | Договор поставки | `03_legal_contract_supply_goods.md` | ✅ PASS |
| 4 | Претензия (late_delivery) | `04_legal_claim_late_delivery.md` + `07_faq_contract_templates.md` | ✅ PASS |
| 5 | Путевой лист (368) | `05_tlog_regulation_waybill.md` | ✅ PASS |
| 6 | **CMR претензия** | **нет `05_tlog_regulation_cmr.md`** | ❌ **FAIL** — уйдёт в refusal или подменит CMR Уставом АТ |
| 7 | ПДн при приёме | `06_comp_policy_pdp.md` + `07_faq_pdp.md` | ✅ PASS |
| 8 | Коммерческая тайна + NDA сотрудника | `06_comp_policy_commercial_secret.md` + `01_hr_pol_confidentiality_emp.md` + `03_legal_contract_ndc.md` (контрагент, не employee) | ⚠️ Частично — employee NDA отсутствует, ответ соберётся из commercial_secret + employee confidentiality policy |
| 9 | Литий морем (refusal) | нет sea-transport | ✅ PASS (как и задумано, refusal сработает) |
| 10 | Франшиза (refusal) | нет franchise | ✅ PASS |
| 11 | Приказ о приёме (draft) | `02_hr_tmp_employment_order.md` + `01_hr_probation_procedure.md` | ✅ PASS |
| 12 | Приказ об увольнении (field_collection) | `02_hr_tmp_dismissal_order.md` + `01_hr_dismissal_procedure.md` | ✅ PASS |

**Сводно:** 10/12 PASS, 1/12 ослаблен (Q2, Q8), 1/12 FAIL (Q6 CMR).

## Recommended final manifest size

**Цель:** минимизировать число файлов при сохранении 12/12 demo-вопросов рабочими и не выйти из коридора README §MVP «3–50 документов».

### Рекомендация A — точечный fix-pack (минимальное вмешательство)

Добавить 4 файла + убрать 4 для сохранения объёма ≈ current (38 файлов).

**Добавить (4):**
1. `05_tlog_regulation_cmr.md` — обязательно для Q6.
2. `06_comp_policy_nda_employee.md` — обязательно для Q8.
3. `07_faq_leave.md` — поднимет confidence Q2.
4. `07_faq_dismissal.md` — парный с dismissal_procedure, страховка Q12.

**Убрать (4) — узкие/дублирующие:**
1. `03_legal_contract_customs_broker.md`
2. `03_legal_contract_termination_checklist.md`
3. `04_legal_claim_non_payment.md`
4. `05_tlog_regulation_customs_clearance.md`

**Итог:** 38 − 4 + 4 = **38 файлов**, demo-набор 12/12 PASS.

### Рекомендация B — строгий MVP shortlist

Привести manifest ровно к 30 файлам из `opus_result_corpus.md`. Это требует:
- удалить 14 «additions» (A1–A14);
- добавить 6 «removals» (R1–R6).

Профит: меньше recall-шума на refusal-вопросы (#9, #10), ниже Mistral-embedding cost.
Риск: теряются полезные FAQ-cross-ref (`07_faq_probation.md`, `07_faq_contract_templates.md`), которые в реальности видны в demo-логах как helpful.

### Рекомендация C — расширенный safety set

Текущие 38 + 4 добавления (CMR, NDA_employee, FAQ_leave, FAQ_dismissal) = **42 файла**. Всё ещё в коридоре `[3, 50]` из README, embedding cost растёт ≈ +10%.

### Что выбрать

- Если ingestion долго и/или Mistral квоты впритык → **A (38, swap)**.
- Если приоритет — стабильный demo без сюрпризов → **C (42, additive only)**.
- Если важно «чистый MVP shortlist» в портфолио/отчёте → **B (30)**, но с принятием риска по Q2, Q8.

Дефолт для предстоящего demo: **A**, как самый низкий по риску.

## Verification

- Sets сравнены имена в имена, регистрозависимо (все файлы lowercase, `.md`).
- 24 пересечения проверены вручную по категориям 1–7.
- Mapping demo-вопросов на shortlist взят из `opus_result_demo_questions.md` §«Покрытие категорий MANIFEST».
- Read-only: `manifests/*` и `corpus/*` не изменены.

## Open questions for owner

1. Подтвердить, что Codex согласен с swap-set A (4 in / 4 out) перед re-ingestion — иначе demo Q6 не отработает.
2. Стоимость Mistral embeddings на 42 файла (вариант C) против 38 — есть ли cap на этой неделе?
3. Не пора ли вынести список MVP-файлов из `MVP_CORPUS_FILES.txt` в `manifests/MANIFEST.md` фронтматтер (`mvp_corpus: true`) — единый источник истины?
