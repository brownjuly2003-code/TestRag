# Retrieval regression — controlled zone Q даёт HR-шаблоны (2026-05-17)

## Симптом

`POST /ask {"question":"Что такое controlled zone аэропорта?"}` → top-5 sources:
1. 0.937 `02_hr_tmp_employment_contract.md` (Трудовой договор шаблон)
2. 0.893 `02_hr_tmp_employment_contract.md`
3. 0.868 `02_hr_tmp_remote_work_agreement.md` (Удалёнка шаблон)
4. 0.843 `02_hr_tmp_leave_order.md` (Приказ отпуск)
5. 0.813 `02_hr_tmp_remote_work_agreement.md`

Ожидалось: top-1 = `01_hr_pol_safety.md` (так было раньше с score 0.97).

## Root cause

Aviation profile pass (commit `7c6951a`, 2026-05-16) переписал ВСЕ 200 corpus-файлов под авиагрузовую тематику. Включая HR-шаблоны (`02_hr_tmp_*`). Теперь шаблоны трудового договора содержат:
- ссылки на `controlled_zone_access`
- упоминания AWB/aviation security
- блоки про допуск в контролируемую зону

```sql
select d.file_name, count(*)
from document_chunks c join documents d on c.document_id=d.id
where c.content ilike '%controlled%zone%' or c.content ilike '%controlled_zone_access%'
group by 1 order by 2 desc limit 10;
```

→ aviation tokens равномерно распределены по корпусу:
- `02_hr_tmp_employment_contract.md`: 5 chunks
- `02_hr_tmp_add_agreement.md`: 4 chunks
- `01_hr_pol_harassment.md`: 3 chunks
- ...
- `01_hr_pol_safety.md`: фактически 1 релевантный (по controll-словам)

Шаблоны трудового договора короче и плотнее по aviation-словам → выше vector similarity score → выше в top-K.

## Fix candidates

1. **Re-profile aviation pass (правильный)**: переделать только tlog/safety/comp файлы, оставить HR-шаблоны без aviation-додавления. Требует ре-генерации 60-80 файлов + re-ingest. ~3-5 часов.

2. **Boost section weight**: добавить в Hybrid retriever bonus за совпадение section/file с "safety"/"controlled"/"aviation" для aviation-вопросов. Хрупко (heuristic), но fast.

3. **Re-ranker**: добавить cross-encoder reranker (MS MARCO модель) на top-20. Снимает BM25/vector шум. ~1-2 часа + новая зависимость.

4. **Acceptable regression**: задокументировать как known limitation демо. Юзер видела ответ хороший по содержанию (Mistral сам собрал нужные термины из «не тех» источников). Top-source мало кто проверяет в TG UI.

## Recommended

Fix 4 (документировать) — для портфолио. Демо работает по содержанию. Source quality — нормальная демо-задача «retrieval polish» в Sprint 4.

Memory: добавить в `project_testrag.md`.
