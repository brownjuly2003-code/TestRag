---
doc_id: tlog_regulation_weight_control
title: Порядок взвешивания авиагруза и chargeable weight
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
- Постановление Правительства РФ от 15.12.2021 № 2319 (весовой контроль)
keywords:
- весовой контроль
- осевые нагрузки
- весогабаритный контроль
- штраф
confidentiality: internal
---

# Порядок взвешивания авиагруза и chargeable weight

## Назначение

Установить процедуру взвешивания, контроля осевых нагрузок и соблюдения весовых ограничений. Логист или диспетчер ООО «Северный Контур» применяет документ при выпуске рейса, приёмке груза или закрытии операции; расхождения по маршруту, грузу, весу или пломбам фиксируются актом до передачи груза следующему участнику цепочки.

## Область применения

Документ используется в контуре авиагрузовых операций для оформления и проверки booking, AWB/MAWB/HAWB,
terminal acceptance,
screening record, ULD/pallet build-up sheet, актов и фотофиксации; эскалация в юридический отдел происходит при
повреждении, утрате, offload, missed cutoff, security hold, customs hold, temperature excursion, регрессе
страховщика или споре по наземному плечу first/last mile.

## Термины

- **Рабочий экземпляр «Порядок взвешивания авиагруза и chargeable weight»** — версия документа с датой, владельцем процесса, статусом согласования и приложениями, по которой можно принимать внутреннее решение.
- **Основание применения «Порядок взвешивания авиагруза и chargeable weight»** — заявка, приказ, договор, акт, обращение или иной первичный документ, без которого ассистент не должен формировать окончательный вывод.
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
| `vehicle_number` | Номер транспортного средства | `{{vehicle_number}}` |
| `cargo_weight` | Груза веса | `{{cargo_weight}}` |
| `axle_loads` | Осевой нагрузок | `{{axle_loads}}` |
| `weighbridge_location` | Место весового контроля | `{{weighbridge_location}}` |
| `weighbridge_certificate` | Сертификат весового контроля | `{{weighbridge_certificate}}` |
| `inspector_name` | Наименование инспектора | `{{inspector_name}}` |

### 3. Подготовка текста

Заполнение ведется только по фактическим данным air cargo booking, авиарейса и подтвержденным перевозочным
документам. Поля, не сверенные с AWB/MAWB/HAWB, terminal log, актом или фотофиксацией, сохраняются как
`{{...}}`; данные авиарейса, airport pair, водитель наземного плеча и cargo не подставляются по предыдущим
рейсам без отдельной проверки.

### 4. Текст шаблона

```
Порядок взвешивания авиагруза и chargeable weight

1. Исходные параметры air cargo операции
- Booking: {{booking_number}}
- AWB/MAWB/HAWB: {{awb_number}} / {{mawb_number}} / {{hawb_number}}
- Аэропорт отправления / назначения: {{airport_origin}} / {{airport_destination}}
- Номер авиарейса и cutoff time: {{flight_number}} / {{cutoff_time}}
- ULD/pallet и chargeable weight: {{uld_or_pallet_id}} / {{chargeable_weight}}
- Terminal handling / security screening: {{terminal_handling_status}} / {{security_screening_status}}
- Номер транспортного средства: {{vehicle_number}}
- Груза веса: {{cargo_weight}}
- Осевой нагрузок: {{axle_loads}}
- Место весового контроля: {{weighbridge_location}}
- Сертификат весового контроля: {{weighbridge_certificate}}
- Наименование инспектора: {{inspector_name}}

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

Операционный документ «Порядок взвешивания авиагруза и chargeable weight» согласуют air cargo operations, диспетчер смены, WMS/склад, terminal representative и carrier/GSA; юрист подключается при damage/loss, offload, missed cutoff, customs/security hold, temperature excursion, terminal charges, insurance regress или инцидент на наземном плече first/last mile. Расхождения по airport pair, flight, AWB/MAWB/HAWB, грузу, пломбам, gross/chargeable weight, температуре, ULD/pallet или комплектности фиксируются актом и фотофиксацией до закрытия air cargo operation.

### 6. Регистрация и хранение

Финальная версия и подтверждающие материалы хранятся в карточке air cargo operation в TMS/WMS/terminal log:
booking, AWB/MAWB/HAWB, cargo manifest, terminal acceptance, screening record, ULD/pallet build-up sheet, акты,
фото, temperature logger, GPS-трек наземного плеча и переписка; доступ получают logistics, terminal/warehouse,
finance, insurance и юристы при споре.


## Рабочие доказательства, сроки и эскалация


- Владелец процесса проверяет, что «Порядок взвешивания авиагруза и chargeable weight» применяется к
  подтвержденной air cargo операции, а не к общей перевозке без booking, AWB/MAWB/HAWB и terminal record.
- Рабочий комплект: gross/chargeable weight, dimensions, reweigh act, scale record и tariff impact. CMR/ТТН,
  GPS и данные водителя используются только для наземного подвоза или вывоза, если этот участок связан с
  airport pair и рейсом.
- Срок реакции: контроль выполняется до выставления счета или спора по chargeable weight; missed cutoff,
  failed screening, offload, customs/security hold, damage/loss или temperature excursion фиксируются в
  TMS/WMS/terminal log с владельцем и следующим сроком.
- Основания для HOLD/STOP: нет scale record, reweigh act, dimensions или согласования перерасчета тарифа.
  Неподтвержденные даты, суммы, персональные данные, пломбы, вес, temperature mode и реквизиты не
  подставляются.
- Маршрут эскалации: warehouse, terminal, carrier/GSA, finance и claims team; спорный RAG-ответ, проект
  письма или операционное решение блокируются до закрытия доказательств и решения владельца процесса.
## Практический сценарий
- Сценарий: диспетчер проверяет специальный груз по «Порядок взвешивания авиагруза и chargeable weight» перед подтверждением booking, terminal slot и наземного плеча first/last mile.
- Проверить: UN number/class, packing instruction, lithium battery status, gross/chargeable weight, dimensions,
  temperature profile, IATA DGR permissions, airline approval, ULD/pallet compatibility и terminal capability.
- Подтвердить источниками: SDS, shipper's declaration, IATA DGR/lithium declaration, temperature record, carrier
  approval, scale ticket, ULD/pallet build-up sheet и securing фото.
- Результат: booking/tender блокируется до carrier approval, terminal capability confirmation, screening plan,
  ULD/pallet approval и monitoring milestones.
- Предметная проверка: признаки «весовой контроль, осевые нагрузки, весогабаритный контроль, штраф» сверяются с исходными документами и не используются как общий ярлык.

## Air cargo профиль документа

- Для «Порядок взвешивания авиагруза и chargeable weight» air cargo профиль строится вокруг подтвержденного
  airport pair, flight number, booking, AWB/MAWB/HAWB, cutoff time, terminal handling, security screening,
  ULD/pallet build-up и chargeable weight.
- Предметная опора документа: gross/chargeable weight, dimensions, reweigh act, scale record и tariff
  impact. Эти факты должны быть видны в TMS/WMS/terminal log, акте, фото, переписке carrier/GSA или
  связанном документе.
- First/last mile описывает только подвоз или вывоз до аэропорта: CMR/ТТН, водитель, GPS и данные ТС не
  заменяют AWB, terminal acceptance, screening/build-up records и cargo manifest.
- Special cargo требует ручной проверки для dangerous goods, lithium batteries, pharma/cold chain,
  perishables, oversized и valuable cargo; HOLD наступает, если нет scale record, reweigh act, dimensions
  или согласования перерасчета тарифа.
- Эскалация идет через warehouse, terminal, carrier/GSA, finance и claims team, чтобы документ не
  превращался в общий транспортный шаблон без авиационных доказательств.
## Правила ответа RAG-ассистента

- Использовать документ как источник типа «регламент» по теме «Порядок взвешивания авиагруза и chargeable weight» только при фактическом совпадении запроса с предметом документа.
- Перед ответом проверить: airport origin/destination, flight number, booking, AWB/MAWB/HAWB, cutoff time,
  terminal acceptance, security screening, ULD/pallet, gross/chargeable weight, shipper/consignee, carrier/GSA,
  special cargo status;
  для first/last mile проверить ТС, водителя, terminal pass, CMR/ТТН, пломбы, фото, GPS и temperature logger;
  класс опасности/температуру/габариты/chargeable weight/ULD limits и разрешения.
- Если фактов по «Порядок взвешивания авиагруза и chargeable weight» не хватает, вернуть уточняющие вопросы; даты, суммы, доступы и реквизиты оставлять неподтвержденными до проверки.
- Споры, расчеты, санкции, защищенные категории и персональные данные передавать на ручную проверку.

## Доказательства и источники для ответа

- договор air cargo/экспедиции, booking confirmation, AWB/MAWB/HAWB, cargo manifest и terminal acceptance record.
- данные груза: gross/chargeable weight, dimensions, packaging, marking/labels, temperature mode, dangerous
  goods/lithium status, пломбы, ULD/pallet и фото.
- SDS, shipper's declaration, temperature log, carrier/terminal approval, scale ticket, ULD/pallet build-up
  sheet и securing фото.
- ключевые признаки документа: весовой контроль, осевые нагрузки, весогабаритный контроль, штраф.
- нормативные ориентиры: Воздушный кодекс РФ; Постановление Правительства РФ от 15.12.2021 № 2319 (весовой контроль).

## Типовые пользовательские запросы

| Запрос пользователя | Безопасная реакция ассистента |
|---------------------|-------------------------------|
| Что проверить по рейсу? | Airport pair, flight, booking, AWB, cutoff, terminal status, cargo, пломбы и фото. |
| Кто отвечает за ущерб или просрочку? | Без AWB, terminal timestamps, актов, фото и carrier evidence не решать. |
| Какие факты нужны для «Порядок взвешивания авиагруза и chargeable weight»? | Перечислить недостающие даты, документы, участников, суммы/сроки и ответственных. |
| Можно ли применять автоматически? | Только после проверки ограничений по «Порядок взвешивания авиагруза и chargeable weight»; при риске или неполных фактах нужна ручная проверка. |

## Ответственные роли

| Роль | Зона ответственности |
|------|----------------------|
| Директор по логистике | утверждает применение правила и дату актуальности источника |
| Логист/диспетчер | проверяет airport pair, flight, booking, AWB, cargo, terminal, carrier/GSA и наземное плечо |
| Терминал / склад / наземное плечо | передает для «Порядок взвешивания авиагруза и chargeable weight» booking, AWB, terminal records, CMR/ТТН и GPS только как first/last mile evidence |
| Юрист/Compliance | оценивает вывод об ответственности без AWB, terminal актов, фото и carrier evidence |

## Риски и ограничения

- Нельзя отвечать без проверки: UN number/class, packing instruction, lithium battery status, gross/chargeable
  weight, dimensions, temperature profile, IATA DGR permissions, airline approval, ULD/pallet compatibility и
  terminal capability.
- ключевые признаки (весовой контроль, осевые нагрузки, весогабаритный контроль, штраф) могут быть неверно применены без документа-основания.
- вывод об ответственности без AWB/MAWB/HAWB, terminal act, фото, flight status, объяснения
  перевозчика/терминала и доказательства наземного плеча.
- расхождение airport pair, flight number, cargo, gross/chargeable weight, пломбы, ULD/pallet или temperature
  mode между booking, AWB/MAWB/HAWB и terminal records.
- air cargo booking выпущен без carrier approval, DGR/cold-chain/oversized разрешений, temperature control,
  screening или chargeable weight check.
- закрытие air cargo operation по устаревшему booking без сверки AWB/MAWB/HAWB, terminal log, screening/build-up
  records, пломб, актов, фото и GPS наземного плеча при наличии.
- ответ без ссылки на профильные источники: SDS, shipper's declaration, IATA DGR/lithium declaration, temperature record, carrier approval, scale ticket, ULD/pallet build-up sheet и securing фото.
## Связанные документы

- `MANIFEST.md`
- `NORMATIVE_SOURCE_MANIFEST.md`
- `05_tlog_contract_transport_air.md`
- `05_tlog_regulation_dispatch.md`
- `05_tlog_checklist_cargo_acceptance.md`
- `04_legal_claim_cargo_damage.md`

## Нормативные ориентиры

- Воздушный кодекс РФ
- Постановление Правительства РФ от 15.12.2021 № 2319 (весовой контроль)

## Критерии качества ответа

- ответ решает именно сценарий «Порядок взвешивания авиагруза и chargeable weight» и не подменяет его общим правилом категории.
- проверено: UN number/class, packing instruction, lithium battery status, gross/chargeable weight, dimensions,
  temperature profile, IATA DGR permissions, airline approval, ULD/pallet compatibility и terminal capability.
- источники подтверждения: SDS, shipper's declaration, IATA DGR/lithium declaration, temperature record, carrier
  approval, scale ticket, ULD/pallet build-up sheet и securing фото.
- учтен профильный риск: air cargo booking/tender выпущен без carrier approval, screening,
  DGR/cold-chain/oversized разрешений, temperature control или chargeable weight confirmation.
- ключевые признаки (весовой контроль, осевые нагрузки, весогабаритный контроль, штраф) использованы только вместе с подтвержденными документами.
- не подставлены airport pair, flight, chargeable weight, пломбы, температура, водитель/ТС наземного плеча,
  CMR/ТТН наземного плеча или акты без air cargo документов.
## Контрольный список

- [ ] запрос сопоставлен с документом «Порядок взвешивания авиагруза и chargeable weight» и типом «регламент»
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
- [ ] недостающие факты по «Порядок взвешивания авиагруза и chargeable weight» вынесены в уточняющие вопросы

## Порядок пересмотра и актуализации

Владелец документа: Директор по логистике. Плановый пересмотр проводится не реже одного раза в 12 месяцев, а
также при изменении законодательства, организационной структуры, маршрута согласования, ответственных ролей или
используемых шаблонов. Изменения вступают в силу после утверждения владельцем процесса и доведения до
сотрудников или контрагентов, которых затрагивает документ.

## История изменений

| Версия | Дата | Изменение | Автор |
|--------|------|-----------|-------|
| 1.0 | 2026-05-15 | Первичная редакция внутреннего документа | Владелец процесса |

> Применять «Порядок взвешивания авиагруза и chargeable weight» после подтверждения владельцем процесса; спорные и нетиповые кейсы требуют ручной проверки.
