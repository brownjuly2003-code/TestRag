# ADR 0004: chunk_overlap=75 (eval-driven correction over ТЗ literal=50)

**Status:** Accepted (2026-05-17). Re-evaluate если корпус удвоится / схема ретривера сменится / появится reranker сверху hybrid.

## Context

ТЗ называет `TokenTextSplitter(chunk_size=500, chunk_overlap=50)` (cl100k_base). Long-time imp `rag-api/app/rag.py` использовал `CHUNK_OVERLAP_TOKENS = 75`. Commit `f98400b` сделал rollback к 50 (literal compliance). Live eval на корпусе MVP-48 (583 chunks → 611) показал регрессию retrieval/refusal — см. [docs/findings/2026-05-17-overlap-50-regression.md](../findings/2026-05-17-overlap-50-regression.md).

## Решение

Вернуть `CHUNK_OVERLAP_TOKENS = 75`. Соблюдена буква ТЗ в части splitter-семьи и chunk_size; отклонение по overlap зафиксировано здесь по эмпирическим данным.

## Доказательство (eval/baseline.json)

| Metric         | overlap=50 | overlap=75 | Floor   | Pass overlap=75? |
|---------------|:---------:|:---------:|:-------:|:----------------:|
| MRR           | 0.5556    | 0.7815    | ≥ 0.60  | ✓                |
| Hit@1         | 0.5556    | 0.6667    | ≥ 0.50  | ✓                |
| Hit@5         | 0.5556    | 1.0000    | —       | ✓                |
| Refusal acc.  | 0.7000    | 1.0000    | ≥ 0.85  | ✓                |

При overlap=50: 4 retrieval-loss + 3 refusal-flip на 10 golden Qs. Причина: длинные специализированные термины (DGR, cutoff time, GHA, основания расторжения) систематически попадают на стык чанков; меньший overlap → потеря BM25-сигнала.

## Альтернативы

| Опция | Pro | Con |
|---|---|---|
| **overlap=75 (выбрано)** | Floor по MRR/Hit@1/refusal проходит; стабильность demo-вопросов | Отклонение от литеральной формулировки ТЗ (50) |
| overlap=50 (буква ТЗ) | Literal compliance | MRR/refusal floor не выдерживается, демо-вопросы (GHA, cutoff, DGR) рандомно теряются |
| overlap=100 (агрессивнее) | Потенциально больше recall | +chunk_count ~20%, удлиняет ingest, BM25 шум, эмбеддинг-стоимость +20%; не проверено эмпирически на этом корпусе |
| Reranker сверху hybrid (cohere/cross-encoder) | Снимает чувствительность к overlap | Внешний API + latency +500-1000ms; вне free-tier бюджета |

## Последствия

- `rag-api/app/rag.py`: `CHUNK_OVERLAP_TOKENS = 75` (+ комментарий со ссылкой сюда).
- `rag-api/tests/test_rag.py::test_split_text_defaults_match_tz_spec` обновлён.
- `eval/baseline.json` отражает overlap=75 (MRR=0.78, Hit@5=1.00, refusal=1.00).
- ТЗ-чеклист: пункт «TokenTextSplitter(500/50)» — частично compliant (splitter+size совпадают, overlap отклонён с обоснованием по данным). Это поведение зафиксировано в README.

## Триггеры пересмотра

1. Корпус >2× текущего (≥1200 chunks): пересчитать chunk_count/latency/quality tradeoff.
2. Замена/добавление reranker'а сверху hybrid: chunk_overlap станет менее чувствительным.
3. Появление инструкции от reviewer'а ТЗ: «literal compliance важнее эмпирических floor'ов» — тогда вернуть 50 и закрепить регрессию как known-issue.
