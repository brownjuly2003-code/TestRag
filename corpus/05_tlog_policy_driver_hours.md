---
doc_id: tlog_policy_driver_hours
title: Политика контроля водителей airport first/last mile
category: Transport and logistics legal docs
document_type: политика
department: Logistics
synthetic_demo: false
source_type: internal_controlled
version: "1.0"
effective_date: '2026-05-15'
owner_role: Директор по логистике
related_normative_sources:
- Воздушный кодекс РФ
- Европейское соглашение ЕСТР (AETR)
- Правила ЕС № 561/2006
keywords:
- режим труда
- отдых
- тахограф
- ЕСТР
confidentiality: internal
---

# Политика контроля водителей airport first/last mile

## Назначение

Установить требования к учету рабочего времени, перерывов и отдыха водителей (ЕСТР/тахограф). Сотрудник логистического контура сверяет air cargo booking, AWB/MAWB/HAWB, аэропорт отправления и назначения, номер рейса, cutoff time, terminal handling, security screening, ULD/pallet build-up, chargeable weight, пломбы, фотофиксацию и GPS/температурные данные наземного плеча; решение о допуске груза к авиарейсу принимается только после устранения расхождений и подтверждения терминала или авиаперевозчика.

## Область применения

Документ «Политика контроля водителей airport first/last mile» применяется при air cargo booking, tender to terminal, terminal acceptance, security screening, ULD/pallet build-up, handover to airline, arrival и recovery. Расхождения по airport pair, flight number, AWB/MAWB/HAWB, chargeable weight, пломбам, температуре, security или customs status фиксируются актом в TMS/WMS/terminal log до закрытия операции и передаются логисту и юристу до претензии или ответа контрагенту.

## Термины

- **Рабочий экземпляр «Политика контроля водителей airport first/last mile»** — версия документа с датой, владельцем процесса, статусом согласования и приложениями, по которой можно принимать внутреннее решение.
- **Основание применения «Политика контроля водителей airport first/last mile»** — заявка, приказ, договор, акт, обращение или иной первичный документ, без которого ассистент не должен формировать окончательный вывод.
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
| `driver_name` | ФИО водителя | `{{driver_name}}` |
| `tachograph_card_number` | Номер карты тахографа | `{{tachograph_card_number}}` |
| `daily_driving_limit` | Дневной лимит управления | `{{daily_driving_limit}}` |
| `weekly_driving_limit` | Недельный лимит управления | `{{weekly_driving_limit}}` |
| `rest_break_requirements` | Требования к перерывам и отдыху | `{{rest_break_requirements}}` |
| `weekly_rest_requirements` | Требования к еженедельному отдыху | `{{weekly_rest_requirements}}` |

### 3. Подготовка текста

Ответственный сотрудник сверяет каждое поле с первичными источниками рейса: air cargo booking, AWB/MAWB/HAWB,
договором перевозки/экспедиции, terminal acceptance, screening record, ULD/pallet build-up sheet, пломбами,
GPS-треком наземного плеча и температурным листом. Незаполненные значения остаются плейсхолдерами `{{...}}` до
устранения расхождений.

### 4. Текст шаблона

```
Политика контроля водителей airport first/last mile

1. Исходные параметры air cargo операции
- Booking: {{booking_number}}
- AWB/MAWB/HAWB: {{awb_number}} / {{mawb_number}} / {{hawb_number}}
- Аэропорт отправления / назначения: {{airport_origin}} / {{airport_destination}}
- Номер авиарейса и cutoff time: {{flight_number}} / {{cutoff_time}}
- ULD/pallet и chargeable weight: {{uld_or_pallet_id}} / {{chargeable_weight}}
- Terminal handling / security screening: {{terminal_handling_status}} / {{security_screening_status}}
- ФИО водителя: {{driver_name}}
- Номер карты тахографа: {{tachograph_card_number}}
- Дневной лимит управления: {{daily_driving_limit}}
- Недельный лимит управления: {{weekly_driving_limit}}
- Требования к перерывам и отдыху: {{rest_break_requirements}}
- Требования к еженедельному отдыху: {{weekly_rest_requirements}}

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

### 6. Регистрация и хранение

Финальная версия и подтверждающие материалы хранятся в карточке air cargo operation в TMS/WMS/terminal log:
booking, AWB/MAWB/HAWB, cargo manifest, terminal acceptance, screening record, ULD/pallet build-up sheet, акты,
фото, temperature logger, GPS-трек наземного плеча и переписка; доступ получают logistics, terminal/warehouse,
finance, insurance и юристы при споре.


## Рабочие доказательства, сроки и эскалация


- Владелец процесса проверяет, что «Политика контроля водителей airport first/last mile» применяется к
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
- Сценарий: диспетчер или механик применяет «Политика контроля водителей airport first/last mile» перед подвозом/вывозом авиагруза на наземном плече first/last mile.
- Проверить: водителя и ТС наземного аэропортового плеча first/last mile, terminal pass, CMR/ТТН
  наземного плеча, пломбы,
  GPS status, temperature logger, tender/recovery time slot и working time limits.
- Подтвердить источниками: CMR/ТТН наземного плеча, terminal pass, чек-лист ТС, GPS track, temperature
  logger, medical/shift check, repair request и defect фото.
- Результат: выпуск рейса подтверждается чек-листом; критичные отклонения передаются механику и руководителю логистики.
- Предметная проверка: признаки «режим труда наземного плеча first/last mile, rest, tachograph, airport slot» сверяются с исходными документами и не используются как общий ярлык.

## Air cargo профиль документа

- Для «Политика контроля водителей airport first/last mile» air cargo профиль строится вокруг
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

- Использовать документ как источник типа «политика» по теме «Политика контроля водителей airport first/last mile» только при фактическом совпадении запроса с предметом документа.
- Перед ответом проверить: airport origin/destination, flight number, booking, AWB/MAWB/HAWB, cutoff time,
  terminal acceptance, security screening, ULD/pallet, gross/chargeable weight, shipper/consignee, carrier/GSA,
  special cargo status; для first/last mile проверить ТС, водителя, terminal pass, CMR/ТТН,
  пломбы, фото, GPS и temperature logger.
- Если фактов по «Политика контроля водителей airport first/last mile» не хватает, вернуть уточняющие вопросы; даты, суммы, доступы и реквизиты оставлять неподтвержденными до проверки.
- Споры, расчеты, санкции, защищенные категории и персональные данные передавать на ручную проверку.

## Доказательства и источники для ответа

- договор air cargo/экспедиции, booking confirmation, AWB/MAWB/HAWB, cargo manifest и terminal acceptance record.
- данные груза: gross/chargeable weight, dimensions, packaging, marking/labels, temperature mode, dangerous
  goods/lithium status, пломбы, ULD/pallet и фото.
- ключевые признаки документа: режим труда наземного плеча first/last mile, rest, tachograph, airport slot.
- нормативные ориентиры: Воздушный кодекс РФ; Европейское соглашение ЕСТР (AETR); Правила ЕС № 561/2006.

## Типовые пользовательские запросы

| Запрос пользователя | Безопасная реакция ассистента |
|---------------------|-------------------------------|
| Что проверить по рейсу? | Airport pair, flight, booking, AWB, cutoff, terminal status, cargo, пломбы и фото. |
| Кто отвечает за ущерб или просрочку? | Без AWB, terminal timestamps, актов, фото и carrier evidence не решать. |
| Какие факты нужны для «Политика контроля водителей airport first/last mile»? | Перечислить недостающие даты, документы, участников, суммы/сроки и ответственных. |
| Можно ли применять автоматически? | Только после проверки ограничений по «Политика контроля водителей airport first/last mile»; при риске или неполных фактах нужна ручная проверка. |

## Ответственные роли

| Роль | Зона ответственности |
|------|----------------------|
| Директор по логистике | утверждает применение правила и дату актуальности источника |
| Логист/диспетчер | проверяет airport pair, flight, booking, AWB, cargo, terminal, carrier/GSA и наземное плечо |
| Терминал / склад / наземное плечо | передает для «Политика контроля водителей airport first/last mile» booking, AWB, terminal records, CMR/ТТН и GPS только как first/last mile evidence |
| Юрист/Compliance | оценивает вывод об ответственности без AWB, terminal актов, фото и carrier evidence |

## Риски и ограничения

- Нельзя отвечать без проверки: водителя и ТС наземного аэропортового плеча first/last mile, terminal pass, CMR/ТТН
  наземного плеча, пломбы, GPS status, temperature logger, tender/recovery time slot и working time limits.
- ключевые признаки (режим труда наземного плеча first/last mile, rest, tachograph, airport slot) могут быть неверно применены без документа-основания.
- вывод об ответственности без AWB/MAWB/HAWB, terminal act, фото, flight status, объяснения
  перевозчика/терминала и доказательства наземного плеча.
- расхождение airport pair, flight number, cargo, gross/chargeable weight, пломбы, ULD/pallet или temperature
  mode между booking, AWB/MAWB/HAWB и terminal records.
- закрытие air cargo operation по устаревшему booking без сверки AWB/MAWB/HAWB, terminal log, screening/build-up
  records, пломб, актов, фото и GPS наземного плеча при наличии.
- ответ без ссылки на профильные источники: CMR/ТТН наземного плеча, terminal pass, чек-лист ТС, GPS
  track, temperature logger, medical/shift check, repair request и defect фото.
## Связанные документы

- `MANIFEST.md`
- `NORMATIVE_SOURCE_MANIFEST.md`
- `05_tlog_contract_transport_air.md`
- `05_tlog_regulation_dispatch.md`
- `05_tlog_checklist_cargo_acceptance.md`
- `04_legal_claim_cargo_damage.md`

## Нормативные ориентиры

- Воздушный кодекс РФ
- Европейское соглашение ЕСТР (AETR)
- Правила ЕС № 561/2006

## Критерии качества ответа

- ответ решает именно сценарий «Политика контроля водителей airport first/last mile» и не подменяет его общим правилом категории.
- проверено: водителя и ТС наземного аэропортового плеча first/last mile, terminal pass, CMR/ТТН
  наземного плеча, пломбы,
  GPS status, temperature logger, tender/recovery time slot и working time limits.
- источники подтверждения: CMR/ТТН наземного плеча, terminal pass, чек-лист ТС, GPS track, temperature
  logger, medical/shift check, repair request и defect фото.
- учтен профильный риск: выезд на наземное плечо first/last mile выполнен без terminal pass,
  проверки ТС/водителя, seal, GPS,
  temperature logger или defect closure.
- ключевые признаки (режим труда наземного плеча first/last mile, rest, tachograph, airport slot) использованы только вместе с подтвержденными документами.
- не подставлены airport pair, flight, chargeable weight, пломбы, температура, водитель/ТС наземного плеча,
  CMR/ТТН наземного плеча или акты без air cargo документов.
## Контрольный список

- [ ] запрос сопоставлен с документом «Политика контроля водителей airport first/last mile» и типом «политика»
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
- [ ] недостающие факты по «Политика контроля водителей airport first/last mile» вынесены в уточняющие вопросы

## Порядок пересмотра и актуализации

Владелец документа: Директор по логистике. Плановый пересмотр проводится не реже одного раза в 12 месяцев, а
также при изменении законодательства, организационной структуры, маршрута согласования, ответственных ролей или
используемых шаблонов. Изменения вступают в силу после утверждения владельцем процесса и доведения до
сотрудников или контрагентов, которых затрагивает документ.

## История изменений

| Версия | Дата | Изменение | Автор |
|--------|------|-----------|-------|
| 1.0 | 2026-05-15 | Первичная редакция внутреннего документа | Владелец процесса |

> Применять «Политика контроля водителей airport first/last mile» после подтверждения владельцем процесса; спорные и нетиповые кейсы требуют ручной проверки.
