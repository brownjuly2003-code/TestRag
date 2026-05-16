# Task 04: Legal Contracts For Air Cargo

## Goal
Перепрофилировать legal contract templates под авиаперевозки, грузовую авиацию, handling, экспедирование и авиагрузовые SLA.

## Scope
- Файлы: `D:\TestRag\corpus\03_legal_*.md`.
- Только corpus-файлы.
- Не менять frontmatter-ключи `doc_id`, `category`, `document_type`, filename.

## Work
1. В договорные документы добавить авиационный предмет:
   - авиаперевозка груза;
   - агентирование авиагрузов;
   - услуги freight forwarder;
   - ground handling;
   - склад временного хранения/грузовой терминал;
   - страхование авиагруза;
   - поставка оборудования/ГСМ/запчастей для авиационного контура, где уместно.
2. Усилить существенные условия:
   - AWB/MAWB/HAWB;
   - booking, flight number, airport of departure/destination;
   - cutoff time, terminal handling, ULD/pallet, chargeable weight;
   - customs/export control;
   - dangerous goods and temperature-controlled cargo.
3. Уточнить приемку и ответственность:
   - акт повреждения/недостачи в терминале;
   - задержка рейса;
   - отказ в приемке груза авиаперевозчиком;
   - нарушение температурного режима;
   - лимиты ответственности и страхование.
4. Улучшить качество текста:
   - убрать универсальные contract-абзацы;
   - проверить падежи;
   - сохранить `{{...}}`;
   - не перегружать каждый договор одинаковым списком терминов.

## Acceptance
- Договоры выглядят как документы компании, работающей с авиаперевозками.
- Существенные условия и доказательства имеют авиационную специфику.
- Оставшиеся road/rail/sea термины используются только там, где это часть мультимодальной цепочки.

## Suggested Verification
```powershell
rg -n "AWB|MAWB|HAWB|flight|рейс|аэропорт|handling|ULD|cutoff" D:\TestRag\corpus\03_legal_*.md
rg -n "`\\{\\.\\.\\.\\}`|ответственный специалист|данных про" D:\TestRag\corpus\03_legal_*.md
```

