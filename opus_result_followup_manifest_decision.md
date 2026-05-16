# Opus Result Followup: Manifest Decision

> Базис: `opus_result_next_manifest_delta.md` (38 в current, 30 в shortlist, 3 варианта A/B/C).
> Назначение: одно решение, без выбора. Передать Codex как ready-to-apply swap-set.
> Никакие правки в `manifests/`, `corpus/` не делались.

## Decision

**Принять вариант A (swap-in-place, итог 38 файлов).**

- Добавить 4 файла из текущего shortlist.
- Удалить 4 файла из текущих additions.
- Net size = 38, без изменения порядка величины Mistral embedding cost.
- Все 12 demo-вопросов (`opus_result_demo_questions.md`) получают рабочий источник.
- Обе критические щели (Q6 CMR, Q8 NDA employee) закрываются.

## Exact swap-set

### Добавить (4)

| Файл | Категория | Зачем | Покрываемый demo-вопрос |
|---|---|---|---|
| `05_tlog_regulation_cmr.md` | 5 (transport regulation) | CMR-конвенция, международные перевозки; нет в текущем manifest | Q6 (CMR претензия) — без файла гарантированный refusal |
| `06_comp_policy_nda_employee.md` | 6 (compliance) | NDA сотрудника, intent LEGAL_NDA (employee scope) | Q8 (commercial secret + NDA сотрудника) |
| `07_faq_leave.md` | 7 (FAQ) | Cross-ref к `01_hr_pol_leave.md` для отпуск 28 дней | Q2 — поднимет confidence с MEDIUM до HIGH |
| `07_faq_dismissal.md` | 7 (FAQ) | Cross-ref к `01_hr_dismissal_procedure.md` | Q12 (field_collection приказ об увольнении) — страховка |

### Удалить (4)

| Файл | Категория | Почему |
|---|---|---|
| `03_legal_contract_customs_broker.md` | 3 (legal contract) | Узкая ниша, не покрыт в demo-вопросах, шумит BM25 на legal-запросах |
| `03_legal_contract_termination_checklist.md` | 3 (legal contract) | Operational checklist, не нормативный документ; снижает precision на retrieval |
| `04_legal_claim_non_payment.md` | 4 (claim) | Полный дубль `04_legal_claim_late_delivery.md` по структуре претензии |
| `05_tlog_regulation_customs_clearance.md` | 5 (transport regulation) | Узкая таможенная ниша; не в demo-вопросах |

## Impact на 12 demo-вопросов

| # | Тема | Было (current 38) | Станет (post-swap 38) |
|---|------|-------------------|------------------------|
| Q1 | Испытание ст.70 | ✅ PASS | ✅ PASS (без изменений) |
| Q2 | Отпуск 28 дней | ⚠️ PASS MEDIUM | ✅ PASS HIGH (через `07_faq_leave.md`) |
| Q3 | Договор поставки | ✅ PASS | ✅ PASS |
| Q4 | Претензия late_delivery | ✅ PASS | ✅ PASS (потеря дубля non_payment не влияет) |
| Q5 | Путевой лист 368 | ✅ PASS | ✅ PASS |
| Q6 | **CMR претензия** | ❌ **FAIL** | ✅ **PASS** |
| Q7 | ПДн при приёме | ✅ PASS | ✅ PASS |
| Q8 | Коммерческая тайна + NDA | ⚠️ Частично | ✅ PASS полностью |
| Q9 | Литий морем (refusal) | ✅ PASS | ✅ PASS (sea-transport всё ещё нет) |
| Q10 | Франшиза (refusal) | ✅ PASS | ✅ PASS |
| Q11 | Приказ о приёме (draft) | ✅ PASS | ✅ PASS |
| Q12 | Приказ об увольнении | ✅ PASS | ✅ PASS (faq_dismissal как страховка) |

**Сводно:** 10/12 → 12/12 PASS. Net change: +Q6, +Q8 укрепил, Q2 поднял confidence.

## Why alternatives rejected

### Вариант B — строгий MVP shortlist (30 файлов)

**Отклонён.** Причины:

- Теряется `07_faq_probation.md` (есть в current, нет в shortlist) — это сильный cross-ref для Q1, главного открывающего demo-вопроса.
- Теряется `07_faq_contract_templates.md` — полезен для Q4 (claim) при intent classification.
- Теряется `02_hr_tmp_remote_work_agreement.md` — это was open question #1 в `opus_result_corpus.md`, добавлен Codex'ом; убирать обратно — регрессия.
- Cost win минимален: 30 vs 38 = -8 файлов, экономия embedding ≈ 20%. Не оправдывает потерю demo-надёжности.
- Корпус-shortlist собирался Opus-1 без знания, какие именно файлы Codex уже включил; current 38 уже отражает накопленный signal — пересборка обнулит этот контекст.

### Вариант C — additive 42 (current 38 + 4 critical)

**Отклонён.** Причины:

- Сохраняет 4 балластных файла (customs_broker, termination_checklist, claim_non_payment, customs_clearance) которые не покрывают ни одного demo-вопроса и зашумляют BM25 на legal/transport кластерах.
- Embedding cost растёт ≈ +10% против swap, без выигрыша в demo-readiness.
- Превышает условный «комфортный» порог в `MVP_CORPUS_FILES.txt` header («Keep this list small enough for demo reindexing and Mistral embedding costs»). 42 формально в коридоре 3–50, но дальше от центра.
- Чем больше файлов в индексе — тем выше вероятность low-relevance source в `sources[]`, что снижает воспринимаемое качество ответа («бот цитирует не то»).

## Ready-to-apply patch для Codex

```diff
 # manifests/MVP_CORPUS_FILES.txt
 # Relative to DOCS_PATH=/app/corpus.
 # Keep this list small enough for demo reindexing and Mistral embedding costs.
 01_hr_pol_leave.md
 01_hr_pol_salary.md
 01_hr_pol_remote_work.md
 01_hr_probation_procedure.md
 01_hr_dismissal_procedure.md
 01_hr_pol_harassment.md
 01_hr_pol_confidentiality_emp.md
 01_hr_pol_corruption.md
 02_hr_tmp_employment_order.md
 02_hr_tmp_leave_order.md
 02_hr_tmp_dismissal_order.md
 02_hr_tmp_add_agreement.md
 02_hr_tmp_employment_contract.md
 02_hr_tmp_remote_work_agreement.md
 03_legal_contract_services_general.md
 03_legal_contract_supply_goods.md
 03_legal_contract_expedition_general.md
 03_legal_contract_cargo_transport_road.md
 03_legal_contract_ndc.md
-03_legal_contract_customs_broker.md
-03_legal_contract_termination_checklist.md
 04_legal_claim_late_delivery.md
 04_legal_claim_defective_goods.md
-04_legal_claim_non_payment.md
 04_legal_claim_cargo_damage.md
 04_legal_reply_late_delivery.md
 04_legal_memo_dispute_risk.md
 05_tlog_contract_transport_road.md
 05_tlog_regulation_waybill.md
+05_tlog_regulation_cmr.md
 05_tlog_regulation_dangerous_goods.md
-05_tlog_regulation_customs_clearance.md
 05_tlog_policy_driver_hours.md
 06_comp_policy_pdp.md
 06_comp_policy_commercial_secret.md
+06_comp_policy_nda_employee.md
 06_comp_policy_incident_response.md
 07_faq_probation.md
+07_faq_leave.md
+07_faq_dismissal.md
 07_faq_contract_templates.md
 07_faq_pdp.md
```

Net: 38 → 38 файлов. После применения требуется re-ingestion (`docker compose up -d --force-recreate rag-api` с `DOCS_PATH=/app/corpus` и `DOCS_MANIFEST_PATH=/app/manifests/MVP_CORPUS_FILES.txt`).

## Verification (для Codex после ingestion)

- `/health` показывает `chunk_count` выше предыдущего baseline 122 (точное значение зависит от chunk_size документов).
- SQL `select count(*) from documents` = 38.
- SQL `select count(*) from document_chunks where document_id in (select id from documents where source_path like '%cmr%')` > 0 — подтверждает, что CMR-файл попал в чанки.
- Demo Q6 (`«В какой срок нужно подать претензию международному автоперевозчику по конвенции CMR?»`) возвращает `refused=false`.

## Pre-conditions (что Codex должен проверить перед swap)

1. Все 4 «добавить» файла существуют в `corpus/` (по `opus_result_corpus.md` они проверены, но между Opus-1 и Opus-2 могли быть переименования — нужна проверка).
2. Файлы из shortlist имеют `frontmatter` с `source_type: synthetic_internal` (для disclaimer-флагов из `opus_result_next_disclaimer.md`).
3. Ingestion-pipeline толерантен к смене состава manifest (на старых записях `documents`/`document_chunks` корректно отрабатывает delete-orphan, иначе будут «висячие» чанки от удалённых 4 файлов).

## Open questions

1. Есть ли в Codex уже patch на `MVP_CORPUS_FILES.txt`, отличный от current 38? Если да — этот diff нужно перенаправить на актуальную базу.
2. Включён ли в pipeline шаг чистки `documents`/`document_chunks` от файлов, которые больше не в manifest? Иначе после swap старые чанки останутся в retrieval.

## Verification (self-check)

- Список Add/Remove явный, по 4 файла, проверены против `opus_result_next_manifest_delta.md`.
- Каждый из 12 demo-вопросов отмаплен на статус до/после.
- Альтернативы B и C отклонены с указанием конкретных потерь / overhead.
- Никакие файлы проекта не редактировались.
