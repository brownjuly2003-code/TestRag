# Eval replay: chunk_overlap 75 → 50 (буква ТЗ)

**Дата:** 2026-05-17
**Контекст:** rollback `f98400b` вернул `CHUNK_OVERLAP_TOKENS = 50` (literal compliance ТЗ).
**Базовая линия (overlap=75):** `.tmp/baseline_overlap75.json`.
**Текущая (overlap=50):** `eval/baseline.json`.

## Aggregate

| Metric          | overlap=75 | overlap=50 | Δ      | Floor    | Pass? |
|-----------------|-----------:|-----------:|-------:|---------:|------:|
| MRR             | 0.7815     | 0.5556     | -0.226 | ≥0.60    | ❌    |
| Hit@1           | 0.6667     | 0.5556     | -0.111 | ≥0.50    | ✓     |
| Hit@5           | 1.0000     | 0.5556     | -0.444 | —        | ⬇     |
| Refusal acc.    | 1.0000     | 0.7000     | -0.300 | ≥0.85    | ❌    |
| chunk_count     | 583        | 611        | +28    | —        | —     |
| avg latency, ms | 6074       | 2810       | −53%   | —        | ✓     |

**Floor:** 2/4. MRR и refusal накопительно ниже минимума.

## Per-question diff

| Вопрос (сокр.)                                     | overlap=75       | overlap=50       | Тип регрессии        |
|----------------------------------------------------|------------------|------------------|----------------------|
| Что такое controlled zone?                         | h1=1 h5=1 ref=Y  | h1=1 h5=1 ref=Y  | —                    |
| Dangerous goods авиатранспортом                    | h1=0 h5=1 ref=Y  | h1=0 h5=0 ref=Y  | RET-LOSS (top-5 → 0) |
| Досрочное расторжение трудового договора           | h1=0 h5=1 ref=Y  | h1=0 h5=0 ref=Y  | RET-LOSS             |
| AWB и MAWB?                                        | h1=1 h5=1 ref=Y  | h1=1 h5=1 ref=N  | REF-FLIP             |
| Испытательный срок по ТК РФ                        | h1=1 h5=1 ref=Y  | h1=1 h5=1 ref=Y  | —                    |
| Максимальный размер ULD                            | h1=1 h5=1 ref=Y  | h1=1 h5=1 ref=Y  | —                    |
| Претензия контрагенту                              | h1=1 h5=1 ref=Y  | h1=1 h5=1 ref=N  | REF-FLIP             |
| Cutoff time в авиагрузовых перевозках              | h1=0 h5=1 ref=Y  | h1=0 h5=0 ref=Y  | RET-LOSS             |
| Литий морем                                        | h1=0 h5=0 ref=Y  | h1=0 h5=0 ref=Y  | (был уже мисс)       |
| GHA?                                               | h1=1 h5=1 ref=Y  | h1=0 h5=0 ref=N  | RET-LOSS + REF-FLIP  |

**Итого:** 4 retrieval-loss, 3 refusal-flip; пострадало 6/10 вопросов.

## Интерпретация

Меньший overlap (50 вместо 75) сдвигает chunk boundaries — длинные специализированные термины и пояснения (DGR-доки, основания расторжения, cutoff time, GHA-glossary) попадают на стык чанков чаще, и BM25 теряет совпадение. Side-effect: confidence просел (0.80 → 0.53), policy чаще выдаёт ответ вместо refusal на корректно-найденный контекст («AWB», «претензия»).

Latency упал почти вдвое — следствие меньшего top-k pool в `HybridRetriever`, но это не компенсирует retrieval-loss.

## Tradeoff — нужно решение владельца ТЗ

| Вариант | Плюс | Минус |
|---|---|---|
| **A: оставить overlap=50** | literal compliance ТЗ | floor по MRR/refusal не выдерживается, демо-вопросы (GHA, cutoff, DGR) рандомно теряются |
| **B: вернуть overlap=75 с обоснованием** | retrieval/refusal floor выдерживается, демо стабильное | расхождение с буквой ТЗ — фиксируется ADR-записью «hybrid retrieval нуждается в overlap=75 для целевого MRR≥0.78 на этом корпусе» |

Рекомендация: B, и в ТЗ добавить footnote с обоснованием по данным. ТЗ — это спецификация качества, а не формула; цифры floor (MRR/Hit/refusal) важнее чем 50 vs 75.

## Текущее состояние

- `eval/baseline.json` сейчас содержит цифры overlap=50 (не закоммичено). Если решение = B, нужно вернуть `CHUNK_OVERLAP_TOKENS = 75` в `rag-api/app/rag.py`, rebuild+reindex, повторно прогнать eval.
- `.tmp/baseline_overlap75.json` сохранён для отката `cp .tmp/baseline_overlap75.json eval/baseline.json`.
