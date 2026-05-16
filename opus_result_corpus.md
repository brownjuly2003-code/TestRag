# Opus Result: Corpus Shortlist Audit

> Source data: `manifests/MANIFEST.md` (200 docs, 7 categories), `manifests/NORMATIVE_SOURCE_MANIFEST.md`, filenames in `corpus/`.
> Scope: select 20-50 файлов для MVP индексации, без редактирования `corpus/`.
> Target: ~30 documents — попадает в MVP rule «индексация 3-50 открытых документов» (README §MVP), покрывает 5 демо-сценариев из demo-runbook + 4 категории документов-черновиков из legal-document-prompts.md.

## Inclusion principle

1. **Priority = high** в MANIFEST — обязательный baseline (есть исключения, см. ниже).
2. Минимум 3 файла из каждой категории, чтобы hybrid retrieval не давал нулевое покрытие при кросс-категорийных вопросах.
3. Каждый файл должен быть «зацеплен» хотя бы за один нормативный источник из NORMATIVE_SOURCE_MANIFEST — иначе ответ будет содержать политику без проверяемой ссылки на ТК/ГК.
4. Templates (категория 2) обязательны для intent `template_draft` из `docs/legal-document-prompts.md` (HR_ORDER_HIRING, HR_ORDER_VACATION, HR_ADDITIONAL_AGREEMENT, HR_EMPLOYMENT_CONTRACT_DRAFT).
5. Claims/replies parity: для каждой претензии в shortlist добавлен парный reply, чтобы demo поток «жалоба → ответ» работал.

## Shortlist (30 файлов)

### Категория 1 — HR internal policies (7 файлов)

| # | Файл | Зачем |
|---|------|-------|
| 1 | `01_hr_pol_leave.md` | Демо вопрос «отпуск» → ТК РФ гл.19; высокая частота в FAQ |
| 2 | `01_hr_pol_salary.md` | Зарплата/выплаты → ТК РФ гл.20; для draft-сценария «приказ об изменении оплаты» |
| 3 | `01_hr_probation_procedure.md` | Главный демо-вопрос из demo-runbook: «ст. 70 ТК РФ испытание»; парный с `02_hr_tmp_employment_order.md` |
| 4 | `01_hr_dismissal_procedure.md` | ТК РФ гл.13; парный с `02_hr_tmp_dismissal_order.md` |
| 5 | `01_hr_pol_remote_work.md` | ТК РФ ст.312.1; покрывает «удаленку» — частый HR-запрос |
| 6 | `01_hr_pol_maternity.md` | ТК РФ ст.260, 255-ФЗ; покрывает декрет — high priority в MANIFEST |
| 7 | `01_hr_pol_injury.md` | 125-ФЗ соцстрахование; редкий, но критичный сценарий, дает ground для compliance |

### Категория 2 — HR templates (5 файлов)

| # | Файл | Зачем |
|---|------|-------|
| 8 | `02_hr_tmp_employment_order.md` | MVP-plan: «генерация черновика по 1 шаблону» — базовый артефакт |
| 9 | `02_hr_tmp_leave_order.md` | Парный к `01_hr_pol_leave.md`; intent HR_ORDER_VACATION |
| 10 | `02_hr_tmp_dismissal_order.md` | Парный к `01_hr_dismissal_procedure.md`; intent HR_ORDER_TERMINATION |
| 11 | `02_hr_tmp_add_agreement.md` | mvp-plan §Tasks упомянут как «1-2 шаблона MVP»; intent HR_ADDITIONAL_AGREEMENT |
| 12 | `02_hr_tmp_employment_contract.md` | intent HR_EMPLOYMENT_CONTRACT_DRAFT (legal-document-prompts.md) |

### Категория 3 — Legal contracts (4 файла)

| # | Файл | Зачем |
|---|------|-------|
| 13 | `03_legal_contract_services_general.md` | intent LEGAL_SERVICE_CONTRACT; ГК РФ гл.39 |
| 14 | `03_legal_contract_supply_goods.md` | intent LEGAL_SUPPLY_CONTRACT; ГК РФ гл.30 |
| 15 | `03_legal_contract_expedition_general.md` | ГК РФ гл.41, 259-ФЗ; ключевой для логистики-клиента |
| 16 | `03_legal_contract_cargo_transport_road.md` | ГК РФ гл.40, 259-ФЗ, Устав АТ; основа для transport-демо |

### Категория 4 — Claims & legal letters (4 файла)

| # | Файл | Зачем |
|---|------|-------|
| 17 | `04_legal_claim_late_delivery.md` | intent LEGAL_CLAIM_LETTER; высокая частота в претензионной работе |
| 18 | `04_legal_reply_late_delivery.md` | intent LEGAL_RESPONSE_LETTER; парный к (17) — для двустороннего демо |
| 19 | `04_legal_claim_cargo_damage.md` | Завязан на CMR/Устав АТ; покрывает logistics dispute |
| 20 | `04_legal_memo_dispute_risk.md` | intent LEGAL_INTERNAL_MEMO |

### Категория 5 — Transport & logistics (4 файла)

| # | Файл | Зачем |
|---|------|-------|
| 21 | `05_tlog_regulation_waybill.md` | Приказ Минтранса №368; путевые листы — частая операционная тема |
| 22 | `05_tlog_regulation_cmr.md` | CMR-конвенция; международные перевозки |
| 23 | `05_tlog_regulation_dangerous_goods.md` | High-priority в MANIFEST; используется для refusal-тестов (узкая ниша) |
| 24 | `05_tlog_policy_driver_hours.md` | 259-ФЗ ст.20; high-priority; смежно с HR (режим труда/отдыха) |

### Категория 6 — Compliance (3 файла)

| # | Файл | Зачем |
|---|------|-------|
| 25 | `06_comp_policy_pdp.md` | 152-ФЗ; high-priority; обязателен для PDP-демо |
| 26 | `06_comp_policy_commercial_secret.md` | 98-ФЗ; high-priority; парный к hr_pol_confidentiality_emp |
| 27 | `06_comp_policy_nda_employee.md` | intent LEGAL_NDA (employee scope); часто запрашиваемый шаблон |

### Категория 7 — FAQ (3 файла)

| # | Файл | Зачем |
|---|------|-------|
| 28 | `07_faq_leave.md` | Поднимает confidence на «отпуск» (cross-ref с pol_leave + tk_rf) |
| 29 | `07_faq_dismissal.md` | Cross-ref с dismissal_procedure |
| 30 | `07_faq_pdp.md` | Поднимает confidence на ПДн (cross-ref с comp_policy_pdp + 152-ФЗ) |

## Rationale by demo scenario

| Demo scenario (demo-runbook.md) | Ключевые файлы из shortlist |
|---|---|
| HR-вопрос (ст.70 ТК РФ испытание) | 3, 8, 28 |
| Legal-вопрос (договор/претензия) | 13, 14, 17, 18 |
| Logistics-вопрос (накладные, CMR) | 21, 22, 16 |
| Compliance-вопрос (ПДн, NDA) | 25, 26, 27, 30 |
| Low-confidence refusal | На 30-файловом срезе не покрыты: морские перевозки, авиаперевозки, франшиза, факторинг, лизинг ТС, цессия → подходят как «узкие» запросы для тестирования отказа |
| Template draft | 8, 9, 10, 11, 12 |

## Excluded categories and why

| Категория / тема | Файлы | Почему исключены |
|---|---|---|
| HR low-priority политики | dress_code, smoking, internal_comm, mental_health, talent_pool, exit_interview, dressing relocation | Тематически узкие, не покрыты нормативной базой в normative manifest — повышают confidence на shallow-запросы и зашумляют BM25 |
| HR job descriptions (кроме hire/leave/term) | job_description_lawyer/hr/driver/accountant | Дублируют политики; шаблоны не нужны для intent HR_JOB_DESCRIPTION в MVP — оставлено только один (логист) можно добавить, но не входит в shortlist |
| Legal niche contracts | franchise, factoring, commission, joint_activity, guarantee, assignment, settlement | low priority в MANIFEST; редкие в реальных запросах; идеальные кандидаты для refusal-тестов (см. ниже) |
| Claims (другие) | service_fail, expedition_breach, customs_delay, lease_breach, ip_infringement | Покрытие парой late_delivery + cargo_damage достаточно для intent LEGAL_CLAIM_LETTER |
| Letters/POA | settlement_proposal, debt_collection, notary_demand, power_of_attorney_* | Не покрыты explicit normative источниками; POA-шаблоны рискованны (доверенности — финальный документ, MVP §Не входит) |
| Transport (rail/air/sea/lease/tire/fuel) | 7 файлов | Узкие сегменты; road + waybill + CMR покрывают 80% запросов |
| Compliance low-priority | cookies, video_surveillance, whistleblower, breach_notification | Не входят в hot path MVP; cookies требует web-присутствия |
| Transport checklists и job descriptions | 7 файлов | Операционные документы — не нормативные; снижают precision retrieval |
| FAQ (остальные) | claims_procedure, commercial_secret, contract_templates, expedition, transport_road, probation, employee_material_liability | Дубль с политиками; включены только «3 high-traffic темы» |

## Refusal-test reserve (НЕ индексировать, использовать в low-confidence demo)

Эти файлы существуют в `corpus/`, но **не добавлять в MVP-индекс**. Они нужны как «control set» — на них demo-вопросы должны получать `refused=true`:

- `05_tlog_contract_transport_sea.md` — морские перевозки
- `05_tlog_contract_transport_air.md` — авиаперевозки
- `03_legal_contract_franchise.md` — франшиза
- `03_legal_contract_factoring.md` — факторинг

Демо-вопрос для refusal (как в `docs/demo-runbook.md`): «Какие правила перевозки лития морем?» — мapping: тема не в shortlist, ожидаемо `refused=true`.

## Verification

- Список из 30 файлов выше, каждый существует в `corpus/` (cross-check по `ls corpus/`).
- Каждый файл имеет соответствие в normative_source_manifest минимум через одну тему (`relevant_topics`).
- `corpus/` не редактировался; result — отдельный файл `opus_result_corpus.md`.
- Покрытие категорий MANIFEST: 1-7 все представлены.
- Размер выборки 30 ∈ [20, 50] — соответствует MVP §Входит «индексация 3-50 открытых документов».

## Open questions for owner

1. Договор `02_hr_tmp_remote_work_agreement.md` (high priority в MANIFEST) — добавить как 31-й? Он нужен для пары с `01_hr_pol_remote_work.md`, но MVP `mvp-plan.md §Tasks` упоминает только 1 шаблон.
2. Включать ли локализованный `06_comp_policy_anticorruption_local.md` или ограничиться `01_hr_pol_corruption.md`? Они частично дублируются.
3. Корпус сейчас содержит документы с `source_type: synthetic_internal` — нужно явно отметить в UI/ответе, что это демо-документы, иначе риск, что заказчик примет synthetic policy за реальный регламент.
