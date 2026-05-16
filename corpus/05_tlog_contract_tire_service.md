---
doc_id: tlog_contract_tire_service
title: Договор ТО транспорта для airport first/last mile
category: Transport and logistics legal docs
document_type: договор оказания услуг
department: Logistics
synthetic_demo: false
source_type: internal_controlled
version: "1.0"
effective_date: '2026-05-15'
owner_role: Директор по логистике
related_normative_sources:
- ГК РФ, глава 39 (оказание услуг)
keywords:
- шиномонтаж
- ТО
- автопарк
- обслуживание
confidentiality: internal
---

# Договор ТО транспорта для airport first/last mile

## Назначение

Шаблон договора на сезонный шиномонтаж и текущий ремонт автопарка. Сотрудник логистического контура сверяет air cargo booking, AWB/MAWB/HAWB, аэропорт отправления и назначения, номер рейса, cutoff time, terminal handling, security screening, ULD/pallet build-up, chargeable weight, пломбы, фотофиксацию и GPS/температурные данные наземного плеча; решение о допуске груза к авиарейсу принимается только после устранения расхождений и подтверждения терминала или авиаперевозчика.

## Область применения

Логист, диспетчер, склад и авиагрузовой терминал используют документ «Договор ТО транспорта для airport first/last mile» для контроля air cargo booking, приемки на терминале, прохождения security screening, build-up, handover to carrier и recovery at destination. Для dangerous goods, lithium batteries, pharma/cold chain, perishables, oversized и valuable cargo добавляется проверка IATA DGR, SDS/shipper's declaration, температурного профиля, специальных разрешений, security status и valuable cargo instructions.

## Термины

- **Рабочий экземпляр «Договор ТО транспорта для airport first/last mile»** — версия документа с датой, владельцем процесса, статусом согласования и приложениями, по которой можно принимать внутреннее решение.
- **Основание применения «Договор ТО транспорта для airport first/last mile»** — заявка, приказ, договор, акт, обращение или иной первичный документ, без которого ассистент не должен формировать окончательный вывод.
- **Air cargo booking** — airport origin/destination, flight number, cutoff time, AWB/MAWB/HAWB, груз,
  gross/chargeable weight, SLA, special cargo restrictions, ULD/pallet и terminal handling requirements.
- **Комплект air cargo документов** — booking confirmation, AWB/MAWB/HAWB, cargo manifest, invoice/packing list,
  terminal acceptance, screening record, ULD/pallet build-up sheet, страховой сертификат, акты; CMR/ТТН, путевой
  лист, водитель и GPS используются только для наземного плеча first/last mile.
- **Событие air cargo рейса** — offload, missed cutoff, failed screening, terminal damage, shortage, ULD split,
  temperature excursion, customs/security hold, delay, rerouting или инцидент наземного плеча с обязательной
  фиксацией доказательств.

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
| `contract_number` | Номер договора | `{{contract_number}}` |
| `contract_date` | Дата договора | `{{contract_date}}` |
| `service_provider_name` | Наименование услуги поставщика | `{{service_provider_name}}` |
| `customer_name` | Наименование заказчика | `{{customer_name}}` |
| `vehicle_list` | Перечень транспортных средств | `{{vehicle_list}}` |
| `service_types` | Услуги типов | `{{service_types}}` |
| `monthly_fee` | Ежемесячное вознаграждение | `{{monthly_fee}}` |
| `response_time` | Время ответа | `{{response_time}}` |

### 3. Подготовка текста

Логист или диспетчер заполняет только подтвержденные поля по booking, AWB/MAWB/HAWB, terminal acceptance,
screening record, CMR/ТТН наземного плеча и фотофиксации. Плейсхолдеры `{{...}}` остаются для несверенных данных
груза, airport pair, пломб, ULD/pallet или ТС наземного плеча; подстановка по аналогии не допускается.

### 4. Текст шаблона

```
Договор ТО транспорта для airport first/last mile

1. Исходные параметры air cargo операции
- Booking: {{booking_number}}
- AWB/MAWB/HAWB: {{awb_number}} / {{mawb_number}} / {{hawb_number}}
- Аэропорт отправления / назначения: {{airport_origin}} / {{airport_destination}}
- Номер авиарейса и cutoff time: {{flight_number}} / {{cutoff_time}}
- ULD/pallet и chargeable weight: {{uld_or_pallet_id}} / {{chargeable_weight}}
- Terminal handling / security screening: {{terminal_handling_status}} / {{security_screening_status}}
- Номер договора: {{contract_number}}
- Дата договора: {{contract_date}}
- Наименование услуги поставщика: {{service_provider_name}}
- Наименование заказчика: {{customer_name}}
- Перечень транспортных средств: {{vehicle_list}}
- Услуги типов: {{service_types}}
- Ежемесячное вознаграждение: {{monthly_fee}}
- Время ответа: {{response_time}}

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

Операционный документ «Договор ТО транспорта для airport first/last mile» согласуют air cargo operations, диспетчер смены, WMS/склад, terminal representative и carrier/GSA; юрист подключается при damage/loss, offload, missed cutoff, customs/security hold, temperature excursion, terminal charges, insurance regress или инцидент на наземном плече first/last mile. Расхождения по airport pair, flight, AWB/MAWB/HAWB, грузу, пломбам, gross/chargeable weight, температуре, ULD/pallet или комплектности фиксируются актом и фотофиксацией до закрытия air cargo operation.

### 6. Подписание и хранение

Финальная версия и подтверждающие материалы хранятся в карточке air cargo operation в TMS/WMS/terminal log:
booking, AWB/MAWB/HAWB, cargo manifest, terminal acceptance, screening record, ULD/pallet build-up sheet, акты,
фото, temperature logger, GPS-трек наземного плеча и переписка; доступ получают logistics, terminal/warehouse,
finance, insurance и юристы при споре.


## Рабочие доказательства, сроки и эскалация


- Владелец процесса проверяет, что «Договор ТО транспорта для airport first/last mile» применяется к
  подтвержденной air cargo операции, а не к общей перевозке без booking, AWB/MAWB/HAWB и terminal record.
- Рабочий комплект: service act, vehicle downtime, airport route impact, spare parts и safety clearance.
  CMR/ТТН, GPS и данные водителя используются только для наземного подвоза или вывоза, если этот участок
  связан с airport pair и рейсом.
- Срок реакции: контроль выполняется до возврата ТС в first/last mile смену; missed cutoff, failed
  screening, offload, customs/security hold, damage/loss или temperature excursion фиксируются в
  TMS/WMS/terminal log с владельцем и следующим сроком.
- Основания для HOLD/STOP: нет акта работ, проверки безопасности, фото или подтверждения готовности ТС.
  Неподтвержденные даты, суммы, персональные данные, пломбы, вес, temperature mode и реквизиты не
  подставляются.
- Маршрут эскалации: fleet service, dispatcher, QHSE, finance и logistics; спорный RAG-ответ, проект письма
  или операционное решение блокируются до закрытия доказательств и решения владельца процесса.
## Практический сценарий
- Сценарий: логистика согласует операцию или договор по конкретному air cargo booking, airport pair, авиарейсу,
  терминалу, авиаперевозчику/GSA или экспедитору.
- Проверить: airport origin/destination, booking, AWB/MAWB/HAWB, flight number, cutoff, chargeable weight,
  carrier/GSA, terminal и airline SLA, liability и claims procedure.
- Подтвердить источниками: booking, договор air cargo/экспедиции, AWB/MAWB/HAWB, terminal acceptance, screening
  record, ULD/pallet sheet, фото, GPS наземного плеча и service act.
- Результат: операция закрывается после сверки документов, KPI/SLA и расхождений в реестре претензий.
- Предметная проверка: признаки «шиномонтаж, ТО, автопарк, обслуживание» сверяются с исходными документами и не используются как общий ярлык.

## Air cargo профиль документа

- Для «Договор ТО транспорта для airport first/last mile» air cargo профиль строится вокруг подтвержденного
  airport pair, flight number, booking, AWB/MAWB/HAWB, cutoff time, terminal handling, security screening,
  ULD/pallet build-up и chargeable weight.
- Предметная опора документа: service act, vehicle downtime, airport route impact, spare parts и safety
  clearance. Эти факты должны быть видны в TMS/WMS/terminal log, акте, фото, переписке carrier/GSA или
  связанном документе.
- First/last mile описывает только подвоз или вывоз до аэропорта: CMR/ТТН, водитель, GPS и данные ТС не
  заменяют AWB, terminal acceptance, screening/build-up records и cargo manifest.
- Special cargo требует ручной проверки для dangerous goods, lithium batteries, pharma/cold chain,
  perishables, oversized и valuable cargo; HOLD наступает, если нет акта работ, проверки безопасности, фото
  или подтверждения готовности ТС.
- Эскалация идет через fleet service, dispatcher, QHSE, finance и logistics, чтобы документ не превращался в
  общий транспортный шаблон без авиационных доказательств.
## Правила ответа RAG-ассистента

- Использовать документ как источник типа «договор оказания услуг» по теме «Договор ТО транспорта для airport first/last mile» только при фактическом совпадении запроса с предметом документа.
- Перед ответом проверить: airport origin/destination, flight number, booking, AWB/MAWB/HAWB, cutoff time,
  terminal acceptance, security screening, ULD/pallet, gross/chargeable weight, shipper/consignee, carrier/GSA,
  special cargo status;
  для first/last mile проверить ТС, водителя, terminal pass, CMR/ТТН, пломбы, фото, GPS и temperature logger;
  ТЗ/SLA, состав услуг, результат, акт, срок устранения замечаний и доступы.
- Если фактов по «Договор ТО транспорта для airport first/last mile» не хватает, вернуть уточняющие вопросы; даты, суммы, доступы и реквизиты оставлять неподтвержденными до проверки.
- Споры, расчеты, санкции, защищенные категории и персональные данные передавать на ручную проверку.

## Доказательства и источники для ответа

- договор air cargo/экспедиции, booking confirmation, AWB/MAWB/HAWB, cargo manifest и terminal acceptance record.
- данные груза: gross/chargeable weight, dimensions, packaging, marking/labels, temperature mode, dangerous
  goods/lithium status, пломбы, ULD/pallet и фото.
- задание, отчет, SLA, акт оказанных услуг, тикеты, переписка и подтверждение результата.
- ключевые признаки документа: шиномонтаж, ТО, автопарк, обслуживание.
- нормативные ориентиры: ГК РФ, глава 39 (оказание услуг).

## Типовые пользовательские запросы

| Запрос пользователя | Безопасная реакция ассистента |
|---------------------|-------------------------------|
| Что проверить по рейсу? | Airport pair, flight, booking, AWB, cutoff, terminal status, cargo, пломбы и фото. |
| Кто отвечает за ущерб или просрочку? | Без AWB, terminal timestamps, актов, фото и carrier evidence не решать. |
| Какие факты нужны для «Договор ТО транспорта для airport first/last mile»? | Перечислить недостающие даты, документы, участников, суммы/сроки и ответственных. |
| Можно ли применять автоматически? | Только после проверки ограничений по «Договор ТО транспорта для airport first/last mile»; при риске или неполных фактах нужна ручная проверка. |

## Ответственные роли

| Роль | Зона ответственности |
|------|----------------------|
| Директор по логистике | утверждает применение правила и дату актуальности источника |
| Логист/диспетчер | проверяет airport pair, flight, booking, AWB, cargo, terminal, carrier/GSA и наземное плечо |
| Терминал / склад / наземное плечо | передает для «Договор ТО транспорта для airport first/last mile» booking, AWB, terminal records, CMR/ТТН и GPS только как first/last mile evidence |
| Юрист/Compliance | оценивает вывод об ответственности без AWB, terminal актов, фото и carrier evidence |

## Риски и ограничения

- Нельзя отвечать без проверки: airport origin/destination, booking, AWB/MAWB/HAWB, flight number, cutoff,
  chargeable weight, carrier/GSA, terminal и airline SLA, liability и claims procedure.
- ключевые признаки (шиномонтаж, ТО, автопарк, обслуживание) могут быть неверно применены без документа-основания.
- вывод об ответственности без AWB/MAWB/HAWB, terminal act, фото, flight status, объяснения
  перевозчика/терминала и доказательства наземного плеча.
- расхождение airport pair, flight number, cargo, gross/chargeable weight, пломбы, ULD/pallet или temperature
  mode между booking, AWB/MAWB/HAWB и terminal records.
- оплата услуг без измеримого результата, акта или подтверждения SLA.
- закрытие air cargo operation по устаревшему booking без сверки AWB/MAWB/HAWB, terminal log, screening/build-up
  records, пломб, актов, фото и GPS наземного плеча при наличии.
- ответ без ссылки на профильные источники: booking, договор air cargo/экспедиции, AWB/MAWB/HAWB, terminal
  acceptance, screening record, ULD/pallet sheet, фото, GPS наземного плеча и service act.
## Связанные документы

- `MANIFEST.md`
- `NORMATIVE_SOURCE_MANIFEST.md`
- `05_tlog_contract_transport_air.md`
- `05_tlog_regulation_dispatch.md`
- `05_tlog_checklist_cargo_acceptance.md`
- `04_legal_claim_cargo_damage.md`

## Нормативные ориентиры

- ГК РФ, глава 39 (оказание услуг)

## Критерии качества ответа

- ответ решает именно сценарий «Договор ТО транспорта для airport first/last mile» и не подменяет его общим правилом категории.
- проверено: airport origin/destination, booking, AWB/MAWB/HAWB, flight number, cutoff, chargeable weight,
  carrier/GSA, terminal и airline SLA, liability и claims procedure.
- источники подтверждения: booking, договор air cargo/экспедиции, AWB/MAWB/HAWB, terminal acceptance, screening
  record, ULD/pallet sheet, фото, GPS наземного плеча и service act.
- учтен профильный риск: оплата или вывод об ответственности сделаны без подтверждения рейса, акта, документов и
  отклонений по маршруту.
- ключевые признаки (шиномонтаж, ТО, автопарк, обслуживание) использованы только вместе с подтвержденными документами.
- не подставлены airport pair, flight, chargeable weight, пломбы, температура, водитель/ТС наземного плеча,
  CMR/ТТН наземного плеча или акты без air cargo документов.
## Контрольный список

- [ ] запрос сопоставлен с документом «Договор ТО транспорта для airport first/last mile» и типом «договор оказания услуг»
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
- [ ] недостающие факты по «Договор ТО транспорта для airport first/last mile» вынесены в уточняющие вопросы

## Порядок пересмотра и актуализации

Владелец документа: Директор по логистике. Плановый пересмотр проводится не реже одного раза в 12 месяцев, а
также при изменении законодательства, организационной структуры, маршрута согласования, ответственных ролей или
используемых шаблонов. Изменения вступают в силу после утверждения владельцем процесса и доведения до
сотрудников или контрагентов, которых затрагивает документ.

## История изменений

| Версия | Дата | Изменение | Автор |
|--------|------|-----------|-------|
| 1.0 | 2026-05-15 | Первичная редакция внутреннего документа | Владелец процесса |

> Применять «Договор ТО транспорта для airport first/last mile» после подтверждения владельцем процесса; спорные и нетиповые кейсы требуют ручной проверки.
