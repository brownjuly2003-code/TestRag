# Sprint 6 #7 — Prev-N-QA retrieval ablation

**Дата:** 2026-05-17
**Статус:** infrastructure done, live A/B отложен на момент когда Docker up.

## Гипотеза

При follow-up-вопросах вроде «А ещё?» / «А срок их действия?» / «Можно ли его продлить?» теряется контекст предыдущего turn'а: query embedding короткий, BM25-токены не пересекаются с целевыми разделами. Prev-N-QA augmentation (concat последних N вопросов в retrieval query) должен поднять Hit@1 на multi-turn кейсах, оставив single-turn нейтральным.

## Реализация

### Код

- `rag-api/app/multiturn.py`:
  - `augment_retrieval_query(current, prev_qas, max_prev=3, include_answers=False)` — конкат через `" | "`. По умолчанию answers НЕ включаются (длинные, размывают вектор).
  - `filter_relevant_prev_qas(qas, skip_refused=True, min_confidence=0.0)` — отбрасывает refusal'ы (бесполезный сигнал).

- `rag-api/app/main.py` `AskRequest.prev_qa_count: int = 0` (opt-in, max=5). При `prev_qa_count > 0` + `telegram_user_id` указан — fetch `store.recent_requests`, filter, augment. Augmented строка идёт ТОЛЬКО в retrieval (`embedding + BM25`). LLM prompt не augmented (защита от дрейфа ответа на off-topic-контексте).

### Защиты

1. **No user_id → no augmentation.** История недоступна, fallback к current question.
2. **Self-skip.** Если recent_requests возвращает текущий же вопрос (race / повтор) — отфильтровывается.
3. **Refusal-skip.** Низко-confidence/refused turns не добавляются.

## Multi-turn golden set

`scripts/eval_multiturn.py`, 5 cases (по 1 setup turn + 1 evaluated):

| # | Setup → Evaluated | Expected files |
|---|---|---|
| 1 | «Что такое controlled zone?» → «А кто туда имеет доступ?» | `01_hr_pol_safety`, `06_comp`, `07_faq_expedition` |
| 2 | «Какие документы для dangerous goods?» → «А срок их действия?» | `06_comp`, `05_tlog`, `07_faq_expedition` |
| 3 | «Что такое AWB и MAWB?» → «А HAWB?» | `05_tlog`, `07_faq_expedition` |
| 4 | «Какой испытательный срок по ТК РФ?» → «Можно ли его продлить?» | `01_hr_probation`, `07_faq_probation`, `external_tk_rf` |
| 5 | «Как составить претензию контрагенту?» → «В какой срок она должна быть рассмотрена?» | `04_legal_cla`, `07_faq_claims_procedure` |

## A/B harness

```bash
docker compose up -d --force-recreate rag-api
python scripts/eval_multiturn.py --output .tmp/eval_multiturn.json
```

Каждый case прогоняется дважды:
- **Arm A:** `prev_qa_count=0` (baseline)
- **Arm B:** `prev_qa_count=2` (Prev-N-QA)

User_id distinct per (case, arm) для изоляции истории.

## Ожидаемая интерпретация

| Сценарий | Что делаем |
|---|---|
| ΔHit@1 ≥ +0.20 на multi-turn | Включить prev_qa_count=2 в n8n Ask RAG body по умолчанию для bot flow. |
| ΔHit@1 в (−0.05, +0.20) | Оставить opt-in; задокументировать как «полезно для специфичных follow-up». |
| ΔHit@1 < −0.05 | Откатить prev_qa_count=2; гипотеза не подтвердилась (шум перевешивает контекст). |

## Live A/B результат (2026-05-17, **финальный — на overlap=75 baseline + MIN_CONFIDENCE=0.25**)

Прогон `python scripts/eval_multiturn.py --output .tmp/eval_multiturn.json` после `docker compose up -d --force-recreate rag-api`:

| Arm | n | Hit@1 | Hit@5 | MRR |
|---|---:|---:|---:|---:|
| **A** `prev_qa_count=0` | 5 | 0.60 | 0.60 | 0.60 |
| **B** `prev_qa_count=2` | 5 | 0.60 | 0.80 | 0.65 |
| **Δ (B−A)** | — | 0.00 | **+0.20** | **+0.05** |

Per-case:

| Case                          | A rank | B rank | Δ |
|-------------------------------|:------:|:------:|:--|
| controlled_zone_followup      | 1      | 1      | — (уже top-1 в A) |
| dangerous_goods_doc_lifespan  | None   | None   | — (vocabulary gap)|
| awb_mawb_breakdown            | 1      | 1      | — (single-turn intent достаточный) |
| probation_extension_check     | 1      | 1      | — |
| claim_procedure_followup      | None   | 4      | ↑ entered top-5 (был miss) |

## Промежуточный прогон на overlap=50 (для истории, не финальный)

| Arm | Hit@1 | Hit@5 | MRR |
|---|---:|---:|---:|
| A | 0.20 | 0.60 | 0.34 |
| B | 0.40 | 0.60 | 0.44 |
| Δ | +0.20 | 0.00 | +0.10 |

Профиль разный: на слабой retrieval-системе (overlap=50, MRR single-turn=0.56) Prev-N-QA продвигает top-1 (controlled_zone: 2→1). На корректной (overlap=75, MRR single-turn=0.78) — улучшает long-tail top-5 (claim_procedure: miss → rank 4). Сигнал augmentation полезен в обоих режимах, ниши разные.

## Решение

ΔHit@1=0, ΔMRR=+0.05, ΔHit@5=+0.20 — попадает в среднюю зону матрицы интерпретации («Δhit@1 в (−0.05, +0.20) → opt-in; задокументировать как «полезно для специфичных follow-up»»). claim_procedure_followup перешёл из miss в top-5 — это и есть та ниша.

**Действие:** оставить `prev_qa_count` opt-in (default=0). Документировать рекомендацию использовать `prev_qa_count=2` для bot flows, где у пользователя стабильно есть predecessor turns. В n8n workflow не включать дефолтно — слишком слабый ΔHit@1 для глобального on.

`.tmp/eval_multiturn.json` финального прогона сохранён.
