# Task 01: Baseline And Aviation Style Guide

## Goal
Подготовить проход по `D:\TestRag\corpus\*.md`: измерить текущее качество корпуса и зафиксировать единый авиационный стиль, чтобы последующие сессии не расходились по терминологии.

## Scope
- Только `D:\TestRag\corpus\*.md`.
- Не менять `MANIFEST.md`, `NORMATIVE_SOURCE_MANIFEST.md`, код, README, docs, docker-compose, тесты и конфиги.
- Не менять `doc_id`, filename, `category`, `document_type`.
- Не коммитить.

## Work
1. Снять baseline: количество файлов, manifest coverage, required quality-секции, broken refs, frontmatter/protected issues, повторяющиеся длинные строки, pytest.
2. Составить внутри рабочего контекста авиационный словарь для следующих сессий:
   - AWB, MAWB, HAWB, авиагруз, грузовой терминал, аэропорт отправления, аэропорт назначения.
   - flight number, booking, cutoff time, slot, ground handling, ULD, pallet build-up, security screening.
   - dangerous goods, lithium batteries, pharma/cold chain, temperature excursion, customs clearance, export control.
   - air carrier, GHA/handling agent, freight forwarder, consignee, shipper, airport pass, controlled zone.
3. Отметить слова, которые нужно осторожно заменять:
   - road/rail/sea-only термины не удалять механически, если документ может покрывать first/last mile.
   - CMR/ТТН оставить только там, где речь о автоподвозе к терминалу; для авиаперевозки использовать AWB/MAWB/HAWB.
4. Проверить 8-10 документов из разных категорий и выписать типовые дефекты качества:
   - универсальные роли;
   - слишком общие доказательства;
   - неавиационные маршруты;
   - неестественные падежи;
   - дублирующиеся абзацы.

## Acceptance
- Есть зафиксированные baseline-метрики до правок.
- Понятен авиационный словарь, который будут использовать следующие сессии.
- Выявлены первые группы документов для перепрофилирования.
- Никакие файлы вне `corpus/*.md` не изменены.

## Suggested Verification
```powershell
git -C D:\TestRag status --short --untracked-files=all
python -m pytest
```

