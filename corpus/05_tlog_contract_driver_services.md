---
doc_id: tlog_contract_driver_services
title: Договор с водителем-ИП на подвоз авиагруза к терминалу
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
- Воздушный кодекс РФ
- Налоговый кодекс РФ (самозанятые, ИП)
keywords:
- самозанятый
- ИП
- водитель
- транспортные услуги
confidentiality: internal
---

# Договор с водителем-ИП на подвоз авиагруза к терминалу

## Назначение

Шаблон договора с самозанятым/ИП на оказание транспортных услуг. Используется в авиагрузовой логистике ООО «Северный Контур» для проверки booking, AWB/MAWB/HAWB, terminal acceptance, screening, ULD/pallet records и акты; эскалация в юридический отдел происходит при damage/loss, offload, missed cutoff, customs/security hold, temperature excursion, terminal charges или insurance regress.

## Область применения

Документ используется в контуре авиагрузовых операций для оформления и проверки booking, AWB/MAWB/HAWB,
terminal acceptance,
screening record, ULD/pallet build-up sheet, актов и фотофиксации; эскалация в юридический отдел происходит при
повреждении, утрате, offload, missed cutoff, security hold, customs hold, temperature excursion, регрессе
страховщика или споре по наземному плечу first/last mile.

## Термины

- **Рабочий экземпляр «Договор с водителем-ИП на подвоз авиагруза к терминалу»** — версия документа с датой, владельцем процесса, статусом согласования и приложениями, по которой можно принимать внутреннее решение.
- **Основание применения «Договор с водителем-ИП на подвоз авиагруза к терминалу»** — заявка, приказ, договор, акт, обращение или иной первичный документ, без которого ассистент не должен формировать окончательный вывод.
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
| `contractor_name` | Наименование исполнителя | `{{contractor_name}}` |
| `customer_name` | Наименование заказчика | `{{customer_name}}` |
| `vehicle_info` | Сведения о транспортном средстве | `{{vehicle_info}}` |
| `service_description` | Описание услуги | `{{service_description}}` |
| `rate_per_km_or_trip` | Ставка за км/рейс | `{{rate_per_km_or_trip}}` |
| `payment_terms` | Условия оплаты | `{{payment_terms}}` |
| `insurance_obligation` | Обязанность по страхованию | `{{insurance_obligation}}` |

### 3. Подготовка текста

Ответственный сотрудник сверяет каждое поле с первичными источниками рейса: air cargo booking, AWB/MAWB/HAWB,
договором перевозки/экспедиции, terminal acceptance, screening record, ULD/pallet build-up sheet, пломбами,
GPS-треком наземного плеча и температурным листом. Незаполненные значения остаются плейсхолдерами `{{...}}` до
устранения расхождений.

### 4. Текст шаблона

```
Договор с водителем-ИП на подвоз авиагруза к терминалу

1. Исходные параметры air cargo операции
- Booking: {{booking_number}}
- AWB/MAWB/HAWB: {{awb_number}} / {{mawb_number}} / {{hawb_number}}
- Аэропорт отправления / назначения: {{airport_origin}} / {{airport_destination}}
- Номер авиарейса и cutoff time: {{flight_number}} / {{cutoff_time}}
- ULD/pallet и chargeable weight: {{uld_or_pallet_id}} / {{chargeable_weight}}
- Terminal handling / security screening: {{terminal_handling_status}} / {{security_screening_status}}
- Номер договора: {{contract_number}}
- Дата договора: {{contract_date}}
- Наименование исполнителя: {{contractor_name}}
- Наименование заказчика: {{customer_name}}
- Сведения о транспортном средстве: {{vehicle_info}}
- Описание услуги: {{service_description}}
- Ставка за км/рейс: {{rate_per_km_or_trip}}
- Условия оплаты: {{payment_terms}}
- Обязанность по страхованию: {{insurance_obligation}}

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

Согласование операции выполняется в режиме реального времени по air cargo чек-листу: booking, AWB/MAWB/HAWB,
flight number, cutoff, terminal acceptance, screening, ULD/pallet build-up, chargeable weight, temperature
logger, пломбы, фото и CMR/ТТН наземного плеча только для first/last mile. Расхождения переводятся в карточку
инцидента TMS/WMS/terminal log с уведомлением air cargo operations, терминала, перевозчика/GSA и юристов при
необходимости.

### 6. Подписание и хранение

Финальная версия и подтверждающие материалы хранятся в карточке air cargo operation в TMS/WMS/terminal log:
booking, AWB/MAWB/HAWB, cargo manifest, terminal acceptance, screening record, ULD/pallet build-up sheet, акты,
фото, temperature logger, GPS-трек наземного плеча и переписка; доступ получают logistics, terminal/warehouse,
finance, insurance и юристы при споре.


## Рабочие доказательства, сроки и эскалация


- Владелец процесса проверяет, что «Договор с водителем-ИП на подвоз авиагруза к терминалу» применяется к
  подтвержденной air cargo операции, а не к общей перевозке без booking, AWB/MAWB/HAWB и terminal record.
- Рабочий комплект: смена водителя, airport pass, CMR/ТТН автоплеча, GPS, пломбы и медосмотр. CMR/ТТН, GPS и
  данные водителя используются только для наземного подвоза или вывоза, если этот участок связан с airport
  pair и рейсом.
- Срок реакции: контроль выполняется до выезда к терминалу или закрытия смены; missed cutoff, failed
  screening, offload, customs/security hold, damage/loss или temperature excursion фиксируются в
  TMS/WMS/terminal log с владельцем и следующим сроком.
- Основания для HOLD/STOP: нет допуска, медосмотра, GPS, пломб или связи с AWB/booking. Неподтвержденные
  даты, суммы, персональные данные, пломбы, вес, temperature mode и реквизиты не подставляются.
- Маршрут эскалации: диспетчер, HR/QHSE, security, terminal и logistics manager; спорный RAG-ответ, проект
  письма или операционное решение блокируются до закрытия доказательств и решения владельца процесса.
## Практический сценарий
- Сценарий: диспетчер или механик применяет «Договор с водителем-ИП на подвоз авиагруза к терминалу» перед подвозом/вывозом авиагруза на наземном плече first/last mile.
- Проверить: водителя и ТС наземного аэропортового плеча first/last mile, terminal pass, CMR/ТТН
  наземного плеча, пломбы,
  GPS status, temperature logger, tender/recovery time slot и working time limits.
- Подтвердить источниками: CMR/ТТН наземного плеча, terminal pass, чек-лист ТС, GPS track, temperature
  logger, medical/shift check, repair request и defect фото.
- Результат: выпуск рейса подтверждается чек-листом; критичные отклонения передаются механику и руководителю логистики.
- Предметная проверка: признаки «самозанятый, ИП, водитель, транспортные услуги» сверяются с исходными документами и не используются как общий ярлык.

## Air cargo профиль документа

- Для «Договор с водителем-ИП на подвоз авиагруза к терминалу» air cargo профиль строится вокруг
  подтвержденного airport pair, flight number, booking, AWB/MAWB/HAWB, cutoff time, terminal handling,
  security screening, ULD/pallet build-up и chargeable weight.
- Предметная опора документа: смена водителя, airport pass, CMR/ТТН автоплеча, GPS, пломбы и медосмотр. Эти
  факты должны быть видны в TMS/WMS/terminal log, акте, фото, переписке carrier/GSA или связанном документе.
- First/last mile описывает только подвоз или вывоз до аэропорта: CMR/ТТН, водитель, GPS и данные ТС не
  заменяют AWB, terminal acceptance, screening/build-up records и cargo manifest.
- Special cargo требует ручной проверки для dangerous goods, lithium batteries, pharma/cold chain,
  perishables, oversized и valuable cargo; HOLD наступает, если нет допуска, медосмотра, GPS, пломб или
  связи с AWB/booking.
- Эскалация идет через диспетчер, HR/QHSE, security, terminal и logistics manager, чтобы документ не
  превращался в общий транспортный шаблон без авиационных доказательств.
## Правила ответа RAG-ассистента

- Использовать документ как источник типа «договор оказания услуг» по теме «Договор с водителем-ИП на подвоз авиагруза к терминалу» только при фактическом совпадении запроса с предметом документа.
- Перед ответом проверить: airport origin/destination, flight number, booking, AWB/MAWB/HAWB, cutoff time,
  terminal acceptance, security screening, ULD/pallet, gross/chargeable weight, shipper/consignee, carrier/GSA,
  special cargo status; для first/last mile проверить ТС, водителя, terminal pass, CMR/ТТН,
  пломбы, фото, GPS и temperature logger.
- Если фактов по «Договор с водителем-ИП на подвоз авиагруза к терминалу» не хватает, вернуть уточняющие вопросы; даты, суммы, доступы и реквизиты оставлять неподтвержденными до проверки.
- Споры, расчеты, санкции, защищенные категории и персональные данные передавать на ручную проверку.

## Доказательства и источники для ответа

- договор air cargo/экспедиции, booking confirmation, AWB/MAWB/HAWB, cargo manifest и terminal acceptance record.
- данные груза: gross/chargeable weight, dimensions, packaging, marking/labels, temperature mode, dangerous
  goods/lithium status, пломбы, ULD/pallet и фото.
- booking, AWB/MAWB/HAWB, terminal log, screening record, акт, фото, GPS наземного плеча и temperature logger.
- задание, отчет, SLA, акт оказанных услуг, тикеты, переписка и подтверждение результата.
- ключевые признаки документа: самозанятый, ИП, водитель, транспортные услуги.
- нормативные ориентиры: ГК РФ, глава 39 (оказание услуг); Воздушный кодекс РФ; Налоговый кодекс РФ (самозанятые, ИП).

## Типовые пользовательские запросы

| Запрос пользователя | Безопасная реакция ассистента |
|---------------------|-------------------------------|
| Что проверить по рейсу? | Airport pair, flight, booking, AWB, cutoff, terminal status, cargo, пломбы и фото. |
| Кто отвечает за ущерб или просрочку? | Без AWB, terminal timestamps, актов, фото и carrier evidence не решать. |
| Какие факты нужны для «Договор с водителем-ИП на подвоз авиагруза к терминалу»? | Перечислить недостающие даты, документы, участников, суммы/сроки и ответственных. |
| Можно ли применять автоматически? | Только после проверки ограничений по «Договор с водителем-ИП на подвоз авиагруза к терминалу»; при риске или неполных фактах нужна ручная проверка. |

## Ответственные роли

| Роль | Зона ответственности |
|------|----------------------|
| Директор по логистике | утверждает применение правила и дату актуальности источника |
| Логист/диспетчер | проверяет airport pair, flight, booking, AWB, cargo, terminal, carrier/GSA и наземное плечо |
| Терминал / склад / наземное плечо | передает для «Договор с водителем-ИП на подвоз авиагруза к терминалу» booking, AWB, terminal records, CMR/ТТН и GPS только как first/last mile evidence |
| Юрист/Compliance | оценивает вывод об ответственности без AWB, terminal актов, фото и carrier evidence |

## Риски и ограничения

- Нельзя отвечать без проверки: водителя и ТС наземного аэропортового плеча first/last mile, terminal pass, CMR/ТТН
  наземного плеча, пломбы, GPS status, temperature logger, tender/recovery time slot и working time limits.
- ключевые признаки (самозанятый, ИП, водитель, транспортные услуги) могут быть неверно применены без документа-основания.
- вывод об ответственности без AWB/MAWB/HAWB, terminal act, фото, flight status, объяснения
  перевозчика/терминала и доказательства наземного плеча.
- расхождение airport pair, flight number, cargo, gross/chargeable weight, пломбы, ULD/pallet или temperature
  mode между booking, AWB/MAWB/HAWB и terminal records.
- несовпадение cargo, airport pair, flight, пломбы, cutoff, terminal SLA или chargeable weight в договоре,
  booking и AWB/MAWB/HAWB.
- оплата услуг без измеримого результата, акта или подтверждения SLA.
- закрытие air cargo operation по устаревшему booking без сверки AWB/MAWB/HAWB, terminal log, screening/build-up
  records, пломб, актов, фото и GPS наземного плеча при наличии.
## Связанные документы

- `MANIFEST.md`
- `NORMATIVE_SOURCE_MANIFEST.md`
- `05_tlog_contract_transport_air.md`
- `05_tlog_regulation_dispatch.md`
- `05_tlog_checklist_cargo_acceptance.md`
- `04_legal_claim_cargo_damage.md`

## Нормативные ориентиры

- ГК РФ, глава 39 (оказание услуг)
- Воздушный кодекс РФ
- Налоговый кодекс РФ (самозанятые, ИП)

## Критерии качества ответа

- ответ решает именно сценарий «Договор с водителем-ИП на подвоз авиагруза к терминалу» и не подменяет его общим правилом категории.
- проверено: водителя и ТС наземного аэропортового плеча first/last mile, terminal pass, CMR/ТТН
  наземного плеча, пломбы,
  GPS status, temperature logger, tender/recovery time slot и working time limits.
- источники подтверждения: CMR/ТТН наземного плеча, terminal pass, чек-лист ТС, GPS track, temperature
  logger, medical/shift check, repair request и defect фото.
- учтен профильный риск: выезд на наземное плечо first/last mile выполнен без terminal pass,
  проверки ТС/водителя, seal, GPS,
  temperature logger или defect closure.
- ключевые признаки (самозанятый, ИП, водитель, транспортные услуги) использованы только вместе с подтвержденными документами.
- не подставлены airport pair, flight, chargeable weight, пломбы, температура, водитель/ТС наземного плеча,
  CMR/ТТН наземного плеча или акты без air cargo документов.
## Контрольный список

- [ ] запрос сопоставлен с документом «Договор с водителем-ИП на подвоз авиагруза к терминалу» и типом «договор оказания услуг»
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
- [ ] недостающие факты по «Договор с водителем-ИП на подвоз авиагруза к терминалу» вынесены в уточняющие вопросы

## Порядок пересмотра и актуализации

Владелец документа: Директор по логистике. Плановый пересмотр проводится не реже одного раза в 12 месяцев, а
также при изменении законодательства, организационной структуры, маршрута согласования, ответственных ролей или
используемых шаблонов. Изменения вступают в силу после утверждения владельцем процесса и доведения до
сотрудников или контрагентов, которых затрагивает документ.

## История изменений

| Версия | Дата | Изменение | Автор |
|--------|------|-----------|-------|
| 1.0 | 2026-05-15 | Первичная редакция внутреннего документа | Владелец процесса |

> Применять «Договор с водителем-ИП на подвоз авиагруза к терминалу» после подтверждения владельцем процесса; спорные и нетиповые кейсы требуют ручной проверки.
