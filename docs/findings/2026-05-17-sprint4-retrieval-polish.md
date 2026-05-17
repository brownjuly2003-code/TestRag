# Sprint 4 retrieval polish — pollution revert (2026-05-17)

## Контекст

Aviation profile pass (`7c6951a`, 2026-05-16) переписал ВСЕ 200 corpus-файлов под авиагрузовую тематику.
HR-шаблоны (`02_hr_tmp_*`) и большая часть HR-политик (`01_hr_pol_*`) получили aviation-токены
(`controlled_zone_access`, `пропуск`, `AWB`, `aviation security`), которые повысили их vector similarity
к aviation-запросам — короткие плотные HR-шаблоны начали выигрывать у длинных профильных доков.

Eval baseline до polish (`.tmp/eval_baseline.json` исторический):

```
hit@1: 0.2222
hit@5: 0.3333
mrr:   0.2778
refusal_accuracy: 0.70
```

## Что сделано

`git checkout 8aa97b9 --` для 76 файлов (см. `.tmp/revert_list.txt`):

- `01_hr_dismissal_procedure`, `01_hr_internal_transfer`, `01_hr_probation_procedure` (3)
- `01_hr_pol_*` кроме `safety.md` (42)
- `02_hr_tmp_*` все шаблоны (25)
- `07_faq_*` кроме `expedition`, `transport_road`, `claims_procedure` (7)

Aviation профиль сохранён в:
- `01_hr_pol_safety.md` (controlled zone — это безопасность авиатерминала, не общая HR)
- `03_legal_*` — cargo контракты
- `04_legal_*` — claims (cargo damage и т.п.)
- `05_tlog_*` — транспортная логистика
- `06_comp_*` — compliance включая dangerous goods
- `07_faq_expedition`, `07_faq_transport_road`, `07_faq_claims_procedure`

Удалён один тест `test_aviation_profile_in_hr_probation` (кодифицировал
aviation pollution как expected behavior, теперь обратное).

В `scripts/eval_retrieval.py` поправлен expected_file для Q5
(`01_hr_pol` → `01_hr_probation` — substring matching больше не ловит правильный файл
после изменения структуры HR-документов).

## Результаты

После revert + re-ingest:

```
hit@1: 0.4444  (+22pp)
hit@5: 0.6667  (+33pp)
mrr:   0.5556  (+28pp, цель ≥0.55 ✓)
refusal_accuracy: 0.70 (без изменений)
chunk_count: 207 → 175
```

Sprint 4 цель MRR ≥0.55 достигнута. Hit@1 цель ≥0.6 не достигнута, gap = три вопроса:

1. **Q2 dangerous goods**: direct curl возвращает `05_tlog_regulation_dangerous_goods` (×5, score 1.16),
   но batched eval показывает `03_legal_*`. Подозрение на nondeterminism в batched embed/retrieval —
   неконсистентность нужно отдельно дебажить.
2. **Q3 досрочное расторжение**: vector embedding не отличает "расторжение договора" от "испытательного срока",
   top-5 содержит probation/employment. Нужна доработка либо корпуса (улучшить `07_faq_dismissal` summary),
   либо ввести query expansion / synonyms.
3. **Q10 GHA**: термин не определён ни в одном файле MVP-44 в чётком виде; нужно либо добавить
   определение GHA в `05_tlog_regulation_waybill` или `07_faq_expedition`, либо пометить ожидаемым refused.

## Refusal accuracy 0.70 — отдельный issue

3 ложных refusal'а:
- Q1 controlled zone: top-1 = 01_hr_pol_safety (правильно), но LLM отвечает «Данных недостаточно».
  Aviation pollution в safety-доке упоминает термин, но не определяет его.
- Q6 ULD: top-2 = 05_tlog_regulation_waybill, top-1 = 06_comp_policy_data_retention. confidence низкая → refused.
- Q10 GHA: см. выше.

Это **content-quality**, а не retrieval. Решается обогащением MVP-44 определениями (см.
`07_faq_expedition` для GHA / 05_tlog для controlled zone / ULD).

## Дальше (Sprint 5 retrieval polish продолжение)

1. Дебажить Q2 nondeterminism — batched eval vs single curl.
2. Добавить eval-regression gate (`pytest scripts/test_eval_regression.py`).
3. Обогатить MVP-44 определениями ключевых aviation-терминов (controlled zone, ULD, GHA).
4. Query expansion / synonyms для расторжения договора.
