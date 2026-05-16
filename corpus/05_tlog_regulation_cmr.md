---
doc_id: tlog_regulation_cmr
title: Порядок оформления AWB/MAWB/HAWB и CMR/ТТН наземного плеча
category: Transport and logistics legal docs
document_type: регламент
department: Logistics
synthetic_demo: false
source_type: internal_controlled
version: "1.0"
effective_date: '2026-05-15'
owner_role: Директор по логистике
related_normative_sources:
- Монреальская конвенция и правила оформления AWB
- Воздушный кодекс РФ
keywords:
- CMR наземного плеча
- накладная
- международная перевозка
- груз
confidentiality: internal
---

# Порядок оформления AWB/MAWB/HAWB и CMR/ТТН наземного плеча

## Назначение

Установить порядок заполнения CMR-накладных, транспортных накладных и электронных аналогов. Сотрудник логистического контура сверяет air cargo booking, AWB/MAWB/HAWB, аэропорт отправления и назначения, номер рейса, cutoff time, terminal handling, security screening, ULD/pallet build-up, chargeable weight, пломбы, фотофиксацию и GPS/температурные данные наземного плеча; решение о допуске груза к авиарейсу принимается только после устранения расхождений и подтверждения терминала или авиаперевозчика.

## Область применения

Документ «Порядок оформления AWB/MAWB/HAWB и CMR/ТТН наземного плеча» применяется при air cargo booking, tender to terminal, terminal acceptance, security screening, ULD/pallet build-up, handover to airline, arrival и recovery. Расхождения по airport pair, flight number, AWB/MAWB/HAWB, chargeable weight, пломбам, температуре, security или customs status фиксируются актом в TMS/WMS/terminal log до закрытия операции и передаются логисту и юристу до претензии или ответа контрагенту.

## Термины

- **Рабочий экземпляр «Порядок оформления AWB/MAWB/HAWB и CMR/ТТН наземного плеча»** — версия документа с датой, владельцем процесса, статусом согласования и приложениями, по которой можно принимать внутреннее решение.
- **Основание применения «Порядок оформления AWB/MAWB/HAWB и CMR/ТТН наземного плеча»** — заявка, приказ, договор, акт, обращение или иной первичный документ, без которого ассистент не должен формировать окончательный вывод.
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
| `cmr_number` | Номер CMR наземного плеча | `{{cmr_number}}` |
| `cmr_date` | Дата CMR наземного плеча | `{{cmr_date}}` |
| `shipper_name` | Наименование грузоотправителя | `{{shipper_name}}` |
| `consignee_name` | Наименование грузополучателя | `{{consignee_name}}` |
| `carrier_name` | Наименование перевозчика | `{{carrier_name}}` |
| `cargo_description` | Описание груза | `{{cargo_description}}` |
| `weight` | Вес | `{{weight}}` |
| `places_count` | Количество мест | `{{places_count}}` |
| `special_instructions` | Особые указания | `{{special_instructions}}` |

### 3. Подготовка текста

Логист или диспетчер заполняет только подтвержденные поля по booking, AWB/MAWB/HAWB, terminal acceptance,
screening record, CMR/ТТН наземного плеча и фотофиксации. Плейсхолдеры `{{...}}` остаются для несверенных данных
груза, airport pair, пломб, ULD/pallet или ТС наземного плеча; подстановка по аналогии не допускается.

### 4. Текст шаблона

```
Порядок оформления AWB/MAWB/HAWB и CMR/ТТН наземного плеча

1. Исходные параметры air cargo операции
- Booking: {{booking_number}}
- AWB/MAWB/HAWB: {{awb_number}} / {{mawb_number}} / {{hawb_number}}
- Аэропорт отправления / назначения: {{airport_origin}} / {{airport_destination}}
- Номер авиарейса и cutoff time: {{flight_number}} / {{cutoff_time}}
- ULD/pallet и chargeable weight: {{uld_or_pallet_id}} / {{chargeable_weight}}
- Terminal handling / security screening: {{terminal_handling_status}} / {{security_screening_status}}
- Номер CMR наземного плеча: {{cmr_number}}
- Дата CMR наземного плеча: {{cmr_date}}
- Наименование грузоотправителя: {{shipper_name}}
- Наименование грузополучателя: {{consignee_name}}
- Наименование перевозчика: {{carrier_name}}
- Описание груза: {{cargo_description}}
- Вес: {{weight}}
- Количество мест: {{places_count}}
- Особые указания: {{special_instructions}}

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

Документ согласуют air cargo operations, диспетчер смены, терминальный представитель и carrier/GSA; служба
безопасности и юрист подключаются при security hold, valuable cargo, dangerous goods/lithium batteries, terminal
damage, temperature excursion, customs delay, инцидент на наземном плече first/last mile или regulator request.

### 6. Регистрация и хранение

Финальная версия и подтверждающие материалы хранятся в карточке air cargo operation в TMS/WMS/terminal log:
booking, AWB/MAWB/HAWB, cargo manifest, terminal acceptance, screening record, ULD/pallet build-up sheet, акты,
фото, temperature logger, GPS-трек наземного плеча и переписка; доступ получают logistics, terminal/warehouse,
finance, insurance и юристы при споре.


## Рабочие доказательства, сроки и эскалация


- Владелец процесса проверяет, что «Порядок оформления AWB/MAWB/HAWB и CMR/ТТН наземного плеча» применяется
  к подтвержденной air cargo операции, а не к общей перевозке без booking, AWB/MAWB/HAWB и terminal record.
- Рабочий комплект: road feeder service, CMR/ТТН, GPS, пломбы, terminal pass и cutoff рейса. CMR/ТТН, GPS и
  данные водителя используются только для наземного подвоза или вывоза, если этот участок связан с airport
  pair и рейсом.
- Срок реакции: контроль выполняется до прибытия к terminal cutoff или ответа по опозданию; missed cutoff,
  failed screening, offload, customs/security hold, damage/loss или temperature excursion фиксируются в
  TMS/WMS/terminal log с владельцем и следующим сроком.
- Основания для HOLD/STOP: CMR/ТТН используются вместо AWB либо нет GPS, пломб, акта или terminal timestamp.
  Неподтвержденные даты, суммы, персональные данные, пломбы, вес, temperature mode и реквизиты не
  подставляются.
- Маршрут эскалации: road carrier, dispatcher, terminal, security и legal claims; спорный RAG-ответ, проект
  письма или операционное решение блокируются до закрытия доказательств и решения владельца процесса.
## Практический сценарий
- Сценарий: логист оформляет перевозочные документы по «Порядок оформления AWB/MAWB/HAWB и CMR/ТТН наземного плеча» до terminal acceptance, cutoff time и выпуском на рейс.
- Проверить: airport origin/destination, flight number, AWB/MAWB/HAWB, booking, places, gross/chargeable weight,
  ULD/pallet, пломбы, shipper, consignee, carrier/GSA, terminal acceptance и акты.
- Подтвердить источниками: AWB/MAWB/HAWB, booking, terminal acceptance, cargo irregularity/damage report, фото,
  пломбы, ULD/pallet record, GPS наземного плеча и подписи.
- Результат: расхождения фиксируются до передачи груза следующему участнику и до выставления претензии.
- Предметная проверка: признаки «AWB/MAWB/HAWB, CMR/ТТН наземного плеча, international air cargo, cargo» сверяются с исходными документами и не используются как общий ярлык.

## Air cargo профиль документа

- Для «Порядок оформления AWB/MAWB/HAWB и CMR/ТТН наземного плеча» air cargo профиль строится вокруг
  подтвержденного airport pair, flight number, booking, AWB/MAWB/HAWB, cutoff time, terminal handling,
  security screening, ULD/pallet build-up и chargeable weight.
- Предметная опора документа: road feeder service, CMR/ТТН, GPS, пломбы, terminal pass и cutoff рейса. Эти
  факты должны быть видны в TMS/WMS/terminal log, акте, фото, переписке carrier/GSA или связанном документе.
- First/last mile описывает только подвоз или вывоз до аэропорта: CMR/ТТН, водитель, GPS и данные ТС не
  заменяют AWB, terminal acceptance, screening/build-up records и cargo manifest.
- Special cargo требует ручной проверки для dangerous goods, lithium batteries, pharma/cold chain,
  perishables, oversized и valuable cargo; HOLD наступает, если CMR/ТТН используются вместо AWB либо нет
  GPS, пломб, акта или terminal timestamp.
- Эскалация идет через road carrier, dispatcher, terminal, security и legal claims, чтобы документ не
  превращался в общий транспортный шаблон без авиационных доказательств.
## Правила ответа RAG-ассистента

- Использовать документ как источник типа «регламент» по теме «Порядок оформления AWB/MAWB/HAWB и CMR/ТТН наземного плеча» только при фактическом совпадении запроса с предметом документа.
- Перед ответом проверить: airport origin/destination, flight number, booking, AWB/MAWB/HAWB, cutoff time,
  terminal acceptance, security screening, ULD/pallet, gross/chargeable weight, shipper/consignee, carrier/GSA,
  special cargo status; для first/last mile проверить ТС, водителя, terminal pass, CMR/ТТН,
  пломбы, фото, GPS и temperature logger.
- Если фактов по «Порядок оформления AWB/MAWB/HAWB и CMR/ТТН наземного плеча» не хватает, вернуть уточняющие вопросы; даты, суммы, доступы и реквизиты оставлять неподтвержденными до проверки.
- Споры, расчеты, санкции, защищенные категории и персональные данные передавать на ручную проверку.

## Доказательства и источники для ответа

- договор air cargo/экспедиции, booking confirmation, AWB/MAWB/HAWB, cargo manifest и terminal acceptance record.
- данные груза: gross/chargeable weight, dimensions, packaging, marking/labels, temperature mode, dangerous
  goods/lithium status, пломбы, ULD/pallet и фото.
- booking, AWB/MAWB/HAWB, terminal log, screening record, акт, фото, GPS наземного плеча и temperature logger.
- ключевые признаки документа: AWB/MAWB/HAWB, CMR/ТТН наземного плеча, international air cargo, cargo.
- нормативные ориентиры: Монреальская конвенция и правила оформления AWB; Воздушный кодекс РФ.

## Типовые пользовательские запросы

| Запрос пользователя | Безопасная реакция ассистента |
|---------------------|-------------------------------|
| Что проверить по рейсу? | Airport pair, flight, booking, AWB, cutoff, terminal status, cargo, пломбы и фото. |
| Кто отвечает за ущерб или просрочку? | Без AWB, terminal timestamps, актов, фото и carrier evidence не решать. |
| Какие факты нужны для «Порядок оформления AWB/MAWB/HAWB и CMR/ТТН наземного плеча»? | Перечислить недостающие даты, документы, участников, суммы/сроки и ответственных. |
| Можно ли применять автоматически? | Только после проверки ограничений по «Порядок оформления AWB/MAWB/HAWB и CMR/ТТН наземного плеча»; при риске или неполных фактах нужна ручная проверка. |

## Ответственные роли

| Роль | Зона ответственности |
|------|----------------------|
| Директор по логистике | утверждает применение правила и дату актуальности источника |
| Логист/диспетчер | проверяет airport pair, flight, booking, AWB, cargo, terminal, carrier/GSA и наземное плечо |
| Терминал / склад / наземное плечо | передает для «Порядок оформления AWB/MAWB/HAWB и CMR/ТТН наземного плеча» booking, AWB, terminal records, CMR/ТТН и GPS только как first/last mile evidence |
| Юрист/Compliance | оценивает вывод об ответственности без AWB, terminal актов, фото и carrier evidence |

## Риски и ограничения

- Нельзя отвечать без проверки: airport origin/destination, flight number, AWB/MAWB/HAWB, booking, places,
  gross/chargeable weight, ULD/pallet, пломбы, shipper, consignee, carrier/GSA, terminal acceptance и акты.
- ключевые признаки (AWB/MAWB/HAWB, CMR/ТТН наземного плеча, international air cargo, cargo) могут быть неверно применены без документа-основания.
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

- Монреальская конвенция и правила оформления AWB
- Воздушный кодекс РФ

## Критерии качества ответа

- ответ решает именно сценарий «Порядок оформления AWB/MAWB/HAWB и CMR/ТТН наземного плеча» и не подменяет его общим правилом категории.
- проверено: airport origin/destination, flight number, AWB/MAWB/HAWB, booking, places, gross/chargeable weight,
  ULD/pallet, пломбы, shipper, consignee, carrier/GSA, terminal acceptance и акты.
- источники подтверждения: AWB/MAWB/HAWB, booking, terminal acceptance, cargo irregularity/damage report, фото,
  пломбы, ULD/pallet record, GPS наземного плеча и подписи.
- учтен профильный риск: данные груза, airport pair, flight, chargeable weight, пломбы или ULD/pallet расходятся
  между booking, AWB/MAWB/HAWB, terminal log и актом.
- ключевые признаки (AWB/MAWB/HAWB, CMR/ТТН наземного плеча, international air cargo, cargo) использованы только вместе с подтвержденными документами.
- не подставлены airport pair, flight, chargeable weight, пломбы, температура, водитель/ТС наземного плеча,
  CMR/ТТН наземного плеча или акты без air cargo документов.
## Контрольный список

- [ ] запрос сопоставлен с документом «Порядок оформления AWB/MAWB/HAWB и CMR/ТТН наземного плеча» и типом «регламент»
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
- [ ] недостающие факты по «Порядок оформления AWB/MAWB/HAWB и CMR/ТТН наземного плеча» вынесены в уточняющие вопросы

## Порядок пересмотра и актуализации

Владелец документа: Директор по логистике. Плановый пересмотр проводится не реже одного раза в 12 месяцев, а
также при изменении законодательства, организационной структуры, маршрута согласования, ответственных ролей или
используемых шаблонов. Изменения вступают в силу после утверждения владельцем процесса и доведения до
сотрудников или контрагентов, которых затрагивает документ.

## История изменений

| Версия | Дата | Изменение | Автор |
|--------|------|-----------|-------|
| 1.0 | 2026-05-15 | Первичная редакция внутреннего документа | Владелец процесса |

> Применять «Порядок оформления AWB/MAWB/HAWB и CMR/ТТН наземного плеча» после подтверждения владельцем процесса; спорные и нетиповые кейсы требуют ручной проверки.
