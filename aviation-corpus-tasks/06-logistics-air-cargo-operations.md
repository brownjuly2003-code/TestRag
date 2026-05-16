# Task 06: Logistics Air Cargo Operations

## Goal
Перепрофилировать transport/logistics документы под air cargo operations и одновременно улучшить конкретику маршрутов, актов, SLA и доказательств.

## Scope
- Файлы: `D:\TestRag\corpus\05_tlog_*.md`.
- Только corpus-файлы.
- Не менять frontmatter-ключи `doc_id`, `category`, `document_type`, filename.

## Work
1. Заменить общий transport-контекст на air cargo:
   - аэропорт отправления/назначения;
   - рейс;
   - AWB/MAWB/HAWB;
   - booking;
   - cutoff time;
   - terminal handling;
   - security screening;
   - ULD/pallet build-up;
   - chargeable weight.
2. Сохранить first/last mile только как часть авиалогистики:
   - автомобильный подвоз к терминалу;
   - CMR/ТТН только для наземного плеча;
   - GPS/пломбы/водитель только для доставки до/из аэропорта.
3. Усилить специальные грузы:
   - dangerous goods;
   - lithium batteries;
   - pharma/cold chain;
   - perishables;
   - oversized cargo;
   - valuable cargo.
4. Улучшить документы:
   - чеклисты сделать операционными, с четкими stop/go критериями;
   - договоры сделать авиационными по предмету и приложениям;
   - регламенты привязать к TMS/WMS/терминальному журналу.

## Acceptance
- Логистические документы ясно относятся к авиаперевозкам.
- Road/rail/sea термины не доминируют и не конфликтуют с aviation profile.
- В чеклистах есть понятные основания запрета выпуска/приемки.

## Suggested Verification
```powershell
rg -n "AWB|MAWB|HAWB|airport|аэропорт|рейс|cutoff|ULD|screening|terminal" D:\TestRag\corpus\05_tlog_*.md
rg -n "морск|железнодорож|CMR|ТТН" D:\TestRag\corpus\05_tlog_*.md
```

