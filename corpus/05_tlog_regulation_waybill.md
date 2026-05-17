---
doc_id: tlog_regulation_waybill
title: Порядок оформления путевых листов для airport first/last mile
category: Transport and logistics legal docs
document_type: регламент
department: Logistics
synthetic_demo: false
source_type: internal_controlled
version: "1.0"
effective_date: '2026-05-15'
owner_role: Директор по логистике
related_normative_sources:
- Воздушный кодекс РФ
- Приказ Минтранса РФ от 15.10.2020 № 368 (путевые листы)
keywords:
- документ наземного плеча first/last mile
- оформление
- учет
- водитель
confidentiality: internal
---

# Порядок оформления путевых листов для airport first/last mile

## Назначение

Регламентировать заполнение, учет и хранение путевых листов (маршрутных карт). Используется в авиагрузовой логистике ООО «Северный Контур» для проверки booking, AWB/MAWB/HAWB, terminal acceptance, screening, ULD/pallet records и акты; эскалация в юридический отдел происходит при damage/loss, offload, missed cutoff, customs/security hold, temperature excursion, terminal charges или insurance regress.

## Область применения

Документ «Порядок оформления путевых листов для airport first/last mile» применяется в авиагрузовой работе: booking, tender/recovery, terminal acceptance, security screening, ULD/pallet build-up, контроль flight status и закрытие POD. Логист сверяет booking, AWB/MAWB/HAWB, terminal log, cutoff, пломбы, фото, chargeable weight и GPS/CMR/ТТН только для наземного плеча first/last mile до cargo release.

## Термины

- **Рабочий экземпляр «Порядок оформления путевых листов для airport first/last mile»** — версия документа с датой, владельцем процесса, статусом согласования и приложениями, по которой можно принимать внутреннее решение.
- **Основание применения «Порядок оформления путевых листов для airport first/last mile»** — заявка, приказ, договор, акт, обращение или иной первичный документ, без которого ассистент не должен формировать окончательный вывод.
- **Авиарейс/air cargo leg** — операция с booking number, AWB/MAWB/HAWB, airport origin/destination, flight
  number, cutoff time, terminal milestones, грузом, ULD/pallet и ответственные лица; водитель и ТС относятся
  только к first/last mile.
- **Операционное отклонение** — missed cutoff, offload, failed security screening, terminal damage, shortage,
  temperature excursion, ULD/pallet build-up mismatch, chargeable weight discrepancy, customs/security hold или
  потеря GPS на наземном плече.
- **TMS/WMS/terminal log** — запись о booking, AWB/MAWB/HAWB, flight status, terminal acceptance, screening,
  build-up, loading, departure/arrival, фото, temperature/GPS events и решениях air cargo operations.

## Порядок действий

### 1. Инициирование

Логист или air cargo диспетчер регистрирует операцию, указывает airport origin/destination, flight number,
booking, AWB/MAWB/HAWB, груз, gross/chargeable weight, terminal, авиаперевозчика/GSA, экспедитора и наземный
first/last mile при наличии. До оформления проверяются booking confirmation, AWB/MAWB/HAWB, terminal
slot/cutoff, security screening requirements, ULD/pallet plan, temperature logger, пломбы, фотофиксация,
GPS-данные наземного плеча и ограничения по special cargo.

### 2. Обязательные поля

| Поле | Назначение | Пример заполнения |
|------|------------|-------------------|
| `awb_number` | Номер AWB | `{{awb_number}}` |
| `mawb_number` | Номер MAWB | `{{mawb_number}}` |
| `hawb_number` | Номер HAWB | `{{hawb_number}}` |
| `booking_number` | Номер air cargo booking | `{{booking_number}}` |
| `flight_number` | Номер авиарейса | `{{flight_number}}` |
| `airport_origin` | Аэропорт отправления | `{{airport_origin}}` |
| `airport_destination` | Аэропорт назначения | `{{airport_destination}}` |
| `cutoff_time` | Cutoff time терминала | `{{cutoff_time}}` |
| `terminal_handling_status` | Статус terminal handling | `{{terminal_handling_status}}` |
| `security_screening_status` | Статус security screening | `{{security_screening_status}}` |
| `uld_or_pallet_id` | ULD или pallet ID | `{{uld_or_pallet_id}}` |
| `chargeable_weight` | Chargeable weight | `{{chargeable_weight}}` |
| `waybill_number` | Номер накладной | `{{waybill_number}}` |
| `waybill_date` | Дата накладной | `{{waybill_date}}` |
| `driver_name` | ФИО водителя | `{{driver_name}}` |
| `vehicle_number` | Номер транспортного средства | `{{vehicle_number}}` |
| `route` | Маршрут | `{{route}}` |
| `departure_time` | Отправления времени | `{{departure_time}}` |
| `return_time` | Срок возврата | `{{return_time}}` |
| `fuel_amount` | Сумма топлива | `{{fuel_amount}}` |
| `odometer_start` | Одометра начала | `{{odometer_start}}` |
| `odometer_end` | Одометра окончания | `{{odometer_end}}` |

### 3. Подготовка текста

Логист или диспетчер заполняет только подтвержденные поля по booking, AWB/MAWB/HAWB, terminal acceptance,
screening record, CMR/ТТН наземного плеча и фотофиксации. Плейсхолдеры `{{...}}` остаются для несверенных данных
груза, airport pair, пломб, ULD/pallet или ТС наземного плеча; подстановка по аналогии не допускается.

### 4. Текст шаблона

```
Порядок оформления путевых листов для airport first/last mile

1. Исходные параметры air cargo операции
- Booking: {{booking_number}}
- AWB/MAWB/HAWB: {{awb_number}} / {{mawb_number}} / {{hawb_number}}
- Аэропорт отправления / назначения: {{airport_origin}} / {{airport_destination}}
- Номер авиарейса и cutoff time: {{flight_number}} / {{cutoff_time}}
- ULD/pallet и chargeable weight: {{uld_or_pallet_id}} / {{chargeable_weight}}
- Terminal handling / security screening: {{terminal_handling_status}} / {{security_screening_status}}
- Номер накладной: {{waybill_number}}
- Дата накладной: {{waybill_date}}
- ФИО водителя: {{driver_name}}
- Номер транспортного средства: {{vehicle_number}}
- Маршрут: {{route}}
- Отправления времени: {{departure_time}}
- Срок возврата: {{return_time}}
- Сумма топлива: {{fuel_amount}}
- Одометра начала: {{odometer_start}}
- Одометра окончания: {{odometer_end}}

2. Документы для сверки
- договор или заявка: {{contract_ref}};
- AWB/MAWB/HAWB, booking confirmation и CMR/ТТН только для наземного плеча: {{transport_document_ref}};
- Перечень доказательств: {{evidence_list}}.

3. Контрольные действия
3.1. Сверить airport origin/destination, flight number, booking, AWB/MAWB/HAWB, груз, упаковку, gross/chargeable
     weight, cutoff time, terminal SLA и ответственные лица.
3.2. Проверить ограничения по dangerous goods, lithium batteries, pharma/cold chain, perishables, oversized,
     valuable cargo, customs и security screening.
3.3. Зафиксировать отклонения в TMS/WMS/terminal log до terminal acceptance, handover to airline или выпуском из
     терминала назначения.

4. Эскалация
Спор о damage/loss, offload, missed cutoff, customs/security hold, temperature excursion, terminal charges или
SLA penalty передается air cargo operations, терминалу, перевозчику/GSA и юристам.

Ответственный: {{responsible_officer}}
Дата: {{document_date}}
```

### 5. Согласование

Операционный документ «Порядок оформления путевых листов для airport first/last mile» согласуют air cargo operations, диспетчер смены, WMS/склад, terminal representative и carrier/GSA; юрист подключается при damage/loss, offload, missed cutoff, customs/security hold, temperature excursion, terminal charges, insurance regress или инцидент на наземном плече first/last mile. Расхождения по airport pair, flight, AWB/MAWB/HAWB, грузу, пломбам, gross/chargeable weight, температуре, ULD/pallet или комплектности фиксируются актом и фотофиксацией до закрытия air cargo operation.

### 6. Регистрация и хранение

Финальная версия и подтверждающие материалы хранятся в карточке air cargo operation в TMS/WMS/terminal log:
booking, AWB/MAWB/HAWB, cargo manifest, terminal acceptance, screening record, ULD/pallet build-up sheet, акты,
фото, temperature logger, GPS-трек наземного плеча и переписка; доступ получают logistics, terminal/warehouse,
finance, insurance и юристы при споре.


## Рабочие доказательства, сроки и эскалация


- Владелец процесса проверяет, что «Порядок оформления путевых листов для airport first/last mile»
  применяется к подтвержденной air cargo операции, а не к общей перевозке без booking, AWB/MAWB/HAWB и
  terminal record.
- Рабочий комплект: AWB/MAWB/HAWB issue, house/master link, cargo manifest, invoice/packing list и
  correction trail. CMR/ТТН, GPS и данные водителя используются только для наземного подвоза или вывоза,
  если этот участок связан с airport pair и рейсом.
- Срок реакции: контроль выполняется до выпуска авианакладной или корректировки данных; missed cutoff,
  failed screening, offload, customs/security hold, damage/loss или temperature excursion фиксируются в
  TMS/WMS/terminal log с владельцем и следующим сроком.
- Основания для HOLD/STOP: нет master/house связки, shipper/consignee data, cargo description или correction
  approval. Неподтвержденные даты, суммы, персональные данные, пломбы, вес, temperature mode и реквизиты не
  подставляются.
- Маршрут эскалации: documentation desk, forwarder, carrier/GSA, customs и finance; спорный RAG-ответ,
  проект письма или операционное решение блокируются до закрытия доказательств и решения владельца процесса.
## Практический сценарий
- Сценарий: логист оформляет перевозочные документы по «Порядок оформления путевых листов для airport first/last mile» до terminal acceptance, cutoff time и выпуском на рейс.
- Проверить: airport origin/destination, flight number, AWB/MAWB/HAWB, booking, places, gross/chargeable weight,
  ULD/pallet, пломбы, shipper, consignee, carrier/GSA, terminal acceptance и акты.
- Подтвердить источниками: AWB/MAWB/HAWB, booking, terminal acceptance, cargo irregularity/damage report, фото,
  пломбы, ULD/pallet record, GPS наземного плеча и подписи.
- Результат: расхождения фиксируются до передачи груза следующему участнику и до выставления претензии.
- Предметная проверка: признаки «документ наземного плеча first/last mile, terminal pass, GPS, передача водителю» сверяются с исходными документами и не используются как общий ярлык.

## Air cargo профиль документа

- Для «Порядок оформления путевых листов для airport first/last mile» air cargo профиль строится вокруг
  подтвержденного airport pair, flight number, booking, AWB/MAWB/HAWB, cutoff time, terminal handling,
  security screening, ULD/pallet build-up и chargeable weight.
- Предметная опора документа: AWB/MAWB/HAWB issue, house/master link, cargo manifest, invoice/packing list и
  correction trail. Эти факты должны быть видны в TMS/WMS/terminal log, акте, фото, переписке carrier/GSA
  или связанном документе.
- First/last mile описывает только подвоз или вывоз до аэропорта: CMR/ТТН, водитель, GPS и данные ТС не
  заменяют AWB, terminal acceptance, screening/build-up records и cargo manifest.
- Special cargo требует ручной проверки для dangerous goods, lithium batteries, pharma/cold chain,
  perishables, oversized и valuable cargo; HOLD наступает, если нет master/house связки, shipper/consignee
  data, cargo description или correction approval.
- Эскалация идет через documentation desk, forwarder, carrier/GSA, customs и finance, чтобы документ не
  превращался в общий транспортный шаблон без авиационных доказательств.
## Правила ответа RAG-ассистента

- Использовать документ как источник типа «регламент» по теме «Порядок оформления путевых листов для airport first/last mile» только при фактическом совпадении запроса с предметом документа.
- Перед ответом проверить: airport origin/destination, flight number, booking, AWB/MAWB/HAWB, cutoff time,
  terminal acceptance, security screening, ULD/pallet, gross/chargeable weight, shipper/consignee, carrier/GSA,
  special cargo status; для first/last mile проверить ТС, водителя, terminal pass, CMR/ТТН,
  пломбы, фото, GPS и temperature logger.
- Если фактов по «Порядок оформления путевых листов для airport first/last mile» не хватает, вернуть уточняющие вопросы; даты, суммы, доступы и реквизиты оставлять неподтвержденными до проверки.
- Споры, расчеты, санкции, защищенные категории и персональные данные передавать на ручную проверку.

## Доказательства и источники для ответа

- договор air cargo/экспедиции, booking confirmation, AWB/MAWB/HAWB, cargo manifest и terminal acceptance record.
- данные груза: gross/chargeable weight, dimensions, packaging, marking/labels, temperature mode, dangerous
  goods/lithium status, пломбы, ULD/pallet и фото.
- booking, AWB/MAWB/HAWB, terminal log, screening record, акт, фото, GPS наземного плеча и temperature logger.
- ключевые признаки документа: документ наземного плеча first/last mile, terminal pass, GPS, передача водителю.
- нормативные ориентиры: Воздушный кодекс РФ; Приказ Минтранса РФ от 15.10.2020 № 368 (путевые листы).

## Типовые пользовательские запросы

| Запрос пользователя | Безопасная реакция ассистента |
|---------------------|-------------------------------|
| Что проверить по рейсу? | Airport pair, flight, booking, AWB, cutoff, terminal status, cargo, пломбы и фото. |
| Кто отвечает за ущерб или просрочку? | Без AWB, terminal timestamps, актов, фото и carrier evidence не решать. |
| Какие факты нужны для «Порядок оформления путевых листов для airport first/last mile»? | Перечислить недостающие даты, документы, участников, суммы/сроки и ответственных. |
| Можно ли применять автоматически? | Только после проверки ограничений по «Порядок оформления путевых листов для airport first/last mile»; при риске или неполных фактах нужна ручная проверка. |

## Ответственные роли

| Роль | Зона ответственности |
|------|----------------------|
| Директор по логистике | утверждает применение правила и дату актуальности источника |
| Логист/диспетчер | проверяет airport pair, flight, booking, AWB, cargo, terminal, carrier/GSA и наземное плечо |
| Терминал / склад / наземное плечо | передает для «Порядок оформления путевых листов для airport first/last mile» booking, AWB, terminal records, CMR/ТТН и GPS только как first/last mile evidence |
| Юрист/Compliance | оценивает вывод об ответственности без AWB, terminal актов, фото и carrier evidence |

## Риски и ограничения

- Нельзя отвечать без проверки: airport origin/destination, flight number, AWB/MAWB/HAWB, booking, places,
  gross/chargeable weight, ULD/pallet, пломбы, shipper, consignee, carrier/GSA, terminal acceptance и акты.
- ключевые признаки (документ наземного плеча first/last mile, terminal pass, GPS, передача водителю) могут быть неверно применены без документа-основания.
- вывод об ответственности без AWB/MAWB/HAWB, terminal act, фото, flight status, объяснения
  перевозчика/терминала и доказательства наземного плеча.
- расхождение airport pair, flight number, cargo, gross/chargeable weight, пломбы, ULD/pallet или temperature
  mode между booking, AWB/MAWB/HAWB и terminal records.
- несовпадение cargo, airport pair, flight, пломбы, cutoff, terminal SLA или chargeable weight в договоре,
  booking и AWB/MAWB/HAWB.
- закрытие air cargo operation по устаревшему booking без сверки AWB/MAWB/HAWB, terminal log, screening/build-up
  records, пломб, актов, фото и GPS наземного плеча при наличии.
- ответ без ссылки на профильные источники: AWB/MAWB/HAWB, booking, terminal acceptance, cargo
  irregularity/damage report, фото, пломбы, ULD/pallet record, GPS наземного плеча и подписи.
## Связанные документы

- `MANIFEST.md`
- `NORMATIVE_SOURCE_MANIFEST.md`
- `05_tlog_contract_transport_air.md`
- `05_tlog_regulation_dispatch.md`
- `05_tlog_checklist_cargo_acceptance.md`
- `04_legal_claim_cargo_damage.md`

## Нормативные ориентиры

- Воздушный кодекс РФ
- Приказ Минтранса РФ от 15.10.2020 № 368 (путевые листы)

## Критерии качества ответа

- ответ решает именно сценарий «Порядок оформления путевых листов для airport first/last mile» и не подменяет его общим правилом категории.
- проверено: airport origin/destination, flight number, AWB/MAWB/HAWB, booking, places, gross/chargeable weight,
  ULD/pallet, пломбы, shipper, consignee, carrier/GSA, terminal acceptance и акты.
- источники подтверждения: AWB/MAWB/HAWB, booking, terminal acceptance, cargo irregularity/damage report, фото,
  пломбы, ULD/pallet record, GPS наземного плеча и подписи.
- учтен профильный риск: данные груза, airport pair, flight, chargeable weight, пломбы или ULD/pallet расходятся
  между booking, AWB/MAWB/HAWB, terminal log и актом.
- ключевые признаки (документ наземного плеча first/last mile, terminal pass, GPS, передача водителю) использованы только вместе с подтвержденными документами.
- не подставлены airport pair, flight, chargeable weight, пломбы, температура, водитель/ТС наземного плеча,
  CMR/ТТН наземного плеча или акты без air cargo документов.
## Контрольный список

- [ ] запрос сопоставлен с документом «Порядок оформления путевых листов для airport first/last mile» и типом «регламент»
- [ ] проверено: airport origin/destination, flight number, booking, AWB/MAWB/HAWB, terminal, carrier/GSA,
  cargo, ULD/pallet, chargeable weight и наземное плечо first/last mile при наличии
- [ ] собраны доказательства: air cargo contract/expedition order, booking, AWB/MAWB/HAWB, cargo manifest,
  terminal acceptance, screening/build-up records и CMR/ТТН только для наземного плеча
- [ ] дополнительно сверено: gross/chargeable weight, dimensions, packaging, labels/marks, temperature mode,
  dangerous goods/lithium status, пломбы, ULD/pallet и фото
- [ ] оценен риск: вывод об ответственности без AWB/MAWB/HAWB, terminal act, flight status, фото, объяснения
  перевозчика/терминала и доказательства наземного плеча
- [ ] отдельно отмечено ограничение: расхождение airport pair, flight, booking, AWB, chargeable weight, пломбы,
  ULD/pallet или temperature mode между документами и terminal records
- [ ] недостающие факты по «Порядок оформления путевых листов для airport first/last mile» вынесены в уточняющие вопросы

## Глоссарий — AWB, ULD, GHA, cutoff

Краткие определения авиагрузовых терминов, применяемых при оформлении путевых листов и сверке наземного плеча с авиагрузовым рейсом.

### AWB, MAWB, HAWB

- **AWB (Air Waybill, авианакладная)** — основной перевозочный документ воздушной перевозки груза, выпускается авиаперевозчиком на каждую партию. Подтверждает заключение договора авиаперевозки, маршрут, условия и стороны.
- **MAWB (Master Air Waybill)** — авианакладная авиаперевозчика на консолидированную партию.
- **HAWB (House Air Waybill)** — авианакладная экспедитора (NVOCC/freight forwarder) на каждый груз внутри консолидации. Один MAWB объединяет один или несколько HAWB.

### ULD (Unit Load Device)

**ULD (Unit Load Device)** — стандартизированный авиаконтейнер или паллет для консолидации, перевозки и обработки груза. Основные типы и максимальные параметры:

| Тип ULD | Описание | Макс. масса |
|---------|----------|-------------|
| AKE / LD3 | контейнер для широкофюзеляжных | 1 587 кг |
| AKH | LD3-45W (узкофюзеляжные A320-семейство) | 1 134 кг |
| PMC | паллет 88×125 дюймов, 10 футов | 4 626 кг |
| PAG | паллет 88×125 дюймов, 9 футов | 4 626 кг |

Максимальный размер ULD для авиаперевозки определяется типом воздушного судна: для широкофюзеляжного грузового (B777F, B747F) — PMC/PAG до 4 626 кг, для узкофюзеляжного (A320/B737) — только LD-семейство. Стандарт — IATA ULD Regulations.

### GHA (Ground Handling Agent)

**GHA (Ground Handling Agent, наземный оператор)** — наземная обслуживающая организация, выполняющая в аэропорту операции по приёмке, формированию и выдаче авиагрузов от имени авиаперевозчика или экспедитора. GHA обрабатывает AWB/MAWB/HAWB, выполняет build-up/break-down ULD, screening, погрузку-разгрузку, документальное оформление, bonded warehouse, передачу first/last mile перевозчику. Регулируется IATA Standard Ground Handling Agreement (SGHA).

### Cutoff time

**Cutoff time** — крайнее время приёма груза грузовым терминалом для конкретного рейса. Включает три уровня: document cutoff (оформление AWB), cargo cutoff (физическая приёмка), security cutoff (после которого груз идёт усиленным контролем). Для опасных грузов и температурочувствительного груза cutoff устанавливается на 2–4 часа раньше general cutoff. Опоздание относительно cutoff = offload груза на следующий рейс или возврат отправителю.

### Controlled zone

**Controlled zone** — зона ограниченного доступа аэропорта, в которой обрабатываются авиагрузы, ULD и терминальное оборудование. Доступ — только с пропуском и подтверждённым инструктажем aviation security; для DG — дополнительно DG-awareness.

## Порядок пересмотра и актуализации

Владелец документа: Директор по логистике. Плановый пересмотр проводится не реже одного раза в 12 месяцев, а
также при изменении законодательства, организационной структуры, маршрута согласования, ответственных ролей или
используемых шаблонов. Изменения вступают в силу после утверждения владельцем процесса и доведения до
сотрудников или контрагентов, которых затрагивает документ.

## История изменений

| Версия | Дата | Изменение | Автор |
|--------|------|-----------|-------|
| 1.0 | 2026-05-15 | Первичная редакция внутреннего документа | Владелец процесса |

> Применять «Порядок оформления путевых листов для airport first/last mile» после подтверждения владельцем процесса; спорные и нетиповые кейсы требуют ручной проверки.
