# Task 07: Compliance, Security And PDP For Aviation

## Goal
Перепрофилировать compliance/PDP/commercial secret документы под риски авиаперевозок, авиационной безопасности, доступа к данным и санкционного/export-control контроля.

## Scope
- Файлы: `D:\TestRag\corpus\06_comp_*.md`.
- Только corpus-файлы.
- Не менять frontmatter-ключи `doc_id`, `category`, `document_type`, filename.

## Work
1. Добавить aviation compliance контекст:
   - авиационная безопасность;
   - доступ в контролируемые зоны аэропорта;
   - данные грузоотправителей, грузополучателей, водителей, представителей агентов;
   - AWB/booking/customer data;
   - терминальные системы, TMS/WMS, access logs.
2. Усилить санкции и export control:
   - проверка маршрута, страны назначения, грузоотправителя/получателя;
   - dual-use goods;
   - dangerous goods;
   - запрет отгрузки до compliance clearance.
3. Уточнить PDP и commercial secret:
   - матрица доступа к AWB/booking/тарифам/маршрутам;
   - retention по рейсовым документам;
   - incident flow при утечке данных или несанкционированном доступе.
4. Улучшить качество:
   - убрать одинаковые compliance-абзацы;
   - проверить падежи;
   - сделать доказательства и эскалации конкретнее.

## Acceptance
- Compliance-документы отражают авиационные риски, а не только общую обработку данных.
- В каждом документе есть роли доступа, retention или incident flow там, где это применимо.
- Санкционный/export-control риск связан с грузом, маршрутом и контрагентом.

## Suggested Verification
```powershell
rg -n "авиацион|аэропорт|AWB|booking|export control|санкц|controlled|доступ" D:\TestRag\corpus\06_comp_*.md
rg -n "матрица доступа|retention|инцидент|журнал" D:\TestRag\corpus\06_comp_*.md
```

