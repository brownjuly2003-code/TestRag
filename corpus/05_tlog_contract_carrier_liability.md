---
doc_id: tlog_contract_carrier_liability
title: Соглашение об ответственности авиаперевозчика и экспедитора
category: Transport and logistics legal docs
document_type: соглашение
department: Logistics
synthetic_demo: false
source_type: internal_controlled
version: "1.0"
effective_date: '2026-05-15'
owner_role: Директор по логистике
related_normative_sources:
- ГК РФ, глава 40 (перевозка)
- Воздушный кодекс РФ
- Воздушный кодекс РФ и правила воздушных перевозок грузов
keywords:
- ответственность перевозчика
- лимит ответственности
- убытки
confidentiality: internal
---

# Соглашение об ответственности авиаперевозчика и экспедитора

## Назначение

Шаблон соглашения, уточняющего размер и условия ответственности перевозчика за груз. Используется в авиагрузовой логистике ООО «Северный Контур» для проверки booking, AWB/MAWB/HAWB, terminal acceptance, screening, ULD/pallet records и акты; эскалация в юридический отдел происходит при damage/loss, offload, missed cutoff, customs/security hold, temperature excursion, terminal charges или insurance regress.

## Область применения

Документ «Соглашение об ответственности авиаперевозчика и экспедитора» применяется при air cargo booking, tender to terminal, terminal acceptance, security screening, ULD/pallet build-up, handover to airline, arrival и recovery. Расхождения по airport pair, flight number, AWB/MAWB/HAWB, chargeable weight, пломбам, температуре, security или customs status фиксируются актом в TMS/WMS/terminal log до закрытия операции и передаются логисту и юристу до претензии или ответа контрагенту.

## Термины

- **Рабочий экземпляр «Соглашение об ответственности авиаперевозчика и экспедитора»** — версия документа с датой, владельцем процесса, статусом согласования и приложениями, по которой можно принимать внутреннее решение.
- **Основание применения «Соглашение об ответственности авиаперевозчика и экспедитора»** — заявка, приказ, договор, акт, обращение или иной первичный документ, без которого ассистент не должен формировать окончательный вывод.
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
| `agreement_number` | Номер соглашения | `{{agreement_number}}` |
| `agreement_date` | Дата соглашения | `{{agreement_date}}` |
| `carrier_name` | Наименование перевозчика | `{{carrier_name}}` |
| `client_name` | Наименование клиента | `{{client_name}}` |
| `liability_limit_per_kg` | Лимит ответственности за кг | `{{liability_limit_per_kg}}` |
| `liability_limit_per_shipment` | Лимит ответственности за отправку | `{{liability_limit_per_shipment}}` |
| `force_majeure_exclusions` | Исключения из форс-мажора | `{{force_majeure_exclusions}}` |
| `insurance_requirements` | Требования к страхованию | `{{insurance_requirements}}` |

### 3. Подготовка текста

Ответственный сотрудник сверяет каждое поле с первичными источниками рейса: air cargo booking, AWB/MAWB/HAWB,
договором перевозки/экспедиции, terminal acceptance, screening record, ULD/pallet build-up sheet, пломбами,
GPS-треком наземного плеча и температурным листом. Незаполненные значения остаются плейсхолдерами `{{...}}` до
устранения расхождений.

### 4. Текст шаблона

```
Соглашение об ответственности авиаперевозчика и экспедитора

1. Исходные параметры air cargo операции
- Booking: {{booking_number}}
- AWB/MAWB/HAWB: {{awb_number}} / {{mawb_number}} / {{hawb_number}}
- Аэропорт отправления / назначения: {{airport_origin}} / {{airport_destination}}
- Номер авиарейса и cutoff time: {{flight_number}} / {{cutoff_time}}
- ULD/pallet и chargeable weight: {{uld_or_pallet_id}} / {{chargeable_weight}}
- Terminal handling / security screening: {{terminal_handling_status}} / {{security_screening_status}}
- Номер соглашения: {{agreement_number}}
- Дата соглашения: {{agreement_date}}
- Наименование перевозчика: {{carrier_name}}
- Наименование клиента: {{client_name}}
- Лимит ответственности за кг: {{liability_limit_per_kg}}
- Лимит ответственности за отправку: {{liability_limit_per_shipment}}
- Исключения из форс-мажора: {{force_majeure_exclusions}}
- Требования к страхованию: {{insurance_requirements}}

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

Операционный документ «Соглашение об ответственности авиаперевозчика и экспедитора» согласуют air cargo operations, диспетчер смены, WMS/склад, terminal representative и carrier/GSA; юрист подключается при damage/loss, offload, missed cutoff, customs/security hold, temperature excursion, terminal charges, insurance regress или инцидент на наземном плече first/last mile. Расхождения по airport pair, flight, AWB/MAWB/HAWB, грузу, пломбам, gross/chargeable weight, температуре, ULD/pallet или комплектности фиксируются актом и фотофиксацией до закрытия air cargo operation.

### 6. Регистрация и хранение

Финальная версия и подтверждающие материалы хранятся в карточке air cargo operation в TMS/WMS/terminal log:
booking, AWB/MAWB/HAWB, cargo manifest, terminal acceptance, screening record, ULD/pallet build-up sheet, акты,
фото, temperature logger, GPS-трек наземного плеча и переписка; доступ получают logistics, terminal/warehouse,
finance, insurance и юристы при споре.


## Рабочие доказательства, сроки и эскалация


- Владелец процесса проверяет, что «Соглашение об ответственности авиаперевозчика и экспедитора» применяется
  к подтвержденной air cargo операции, а не к общей перевозке без booking, AWB/MAWB/HAWB и terminal record.
- Рабочий комплект: liability cap, AWB conditions, carrier evidence, terminal act и SLA breach. CMR/ТТН, GPS
  и данные водителя используются только для наземного подвоза или вывоза, если этот участок связан с airport
  pair и рейсом.
- Срок реакции: контроль выполняется до расчета ответственности перевозчика; missed cutoff, failed
  screening, offload, customs/security hold, damage/loss или temperature excursion фиксируются в
  TMS/WMS/terminal log с владельцем и следующим сроком.
- Основания для HOLD/STOP: нет AWB conditions, terminal timestamps, актов или объяснения carrier/GSA.
  Неподтвержденные даты, суммы, персональные данные, пломбы, вес, temperature mode и реквизиты не
  подставляются.
- Маршрут эскалации: carrier/GSA, терминал, insurance, finance и legal claims; спорный RAG-ответ, проект
  письма или операционное решение блокируются до закрытия доказательств и решения владельца процесса.
## Практический сценарий
- Сценарий: логистика согласует операцию или договор по конкретному air cargo booking, airport pair, авиарейсу,
  терминалу, авиаперевозчику/GSA или экспедитору.
- Проверить: airport origin/destination, booking, AWB/MAWB/HAWB, flight number, cutoff, chargeable weight,
  carrier/GSA, terminal и airline SLA, liability и claims procedure.
- Подтвердить источниками: booking, договор air cargo/экспедиции, AWB/MAWB/HAWB, terminal acceptance, screening
  record, ULD/pallet sheet, фото, GPS наземного плеча и service act.
- Результат: операция закрывается после сверки документов, KPI/SLA и расхождений в реестре претензий.
- Предметная проверка: признаки «ответственность перевозчика, лимит ответственности, убытки» сверяются с исходными документами и не используются как общий ярлык.

## Air cargo профиль документа

- Для «Соглашение об ответственности авиаперевозчика и экспедитора» air cargo профиль строится вокруг
  подтвержденного airport pair, flight number, booking, AWB/MAWB/HAWB, cutoff time, terminal handling,
  security screening, ULD/pallet build-up и chargeable weight.
- Предметная опора документа: liability cap, AWB conditions, carrier evidence, terminal act и SLA breach.
  Эти факты должны быть видны в TMS/WMS/terminal log, акте, фото, переписке carrier/GSA или связанном
  документе.
- First/last mile описывает только подвоз или вывоз до аэропорта: CMR/ТТН, водитель, GPS и данные ТС не
  заменяют AWB, terminal acceptance, screening/build-up records и cargo manifest.
- Special cargo требует ручной проверки для dangerous goods, lithium batteries, pharma/cold chain,
  perishables, oversized и valuable cargo; HOLD наступает, если нет AWB conditions, terminal timestamps,
  актов или объяснения carrier/GSA.
- Эскалация идет через carrier/GSA, терминал, insurance, finance и legal claims, чтобы документ не
  превращался в общий транспортный шаблон без авиационных доказательств.
## Правила ответа RAG-ассистента

- Использовать документ как источник типа «соглашение» по теме «Соглашение об ответственности авиаперевозчика и экспедитора» только при фактическом совпадении запроса с предметом документа.
- Перед ответом проверить: airport origin/destination, flight number, booking, AWB/MAWB/HAWB, cutoff time,
  terminal acceptance, security screening, ULD/pallet, gross/chargeable weight, shipper/consignee, carrier/GSA,
  special cargo status; для first/last mile проверить ТС, водителя, terminal pass, CMR/ТТН,
  пломбы, фото, GPS и temperature logger.
- Если фактов по «Соглашение об ответственности авиаперевозчика и экспедитора» не хватает, вернуть уточняющие вопросы; даты, суммы, доступы и реквизиты оставлять неподтвержденными до проверки.
- Споры, расчеты, санкции, защищенные категории и персональные данные передавать на ручную проверку.

## Доказательства и источники для ответа

- договор air cargo/экспедиции, booking confirmation, AWB/MAWB/HAWB, cargo manifest и terminal acceptance record.
- данные груза: gross/chargeable weight, dimensions, packaging, marking/labels, temperature mode, dangerous
  goods/lithium status, пломбы, ULD/pallet и фото.
- booking, AWB/MAWB/HAWB, terminal log, screening record, акт, фото, GPS наземного плеча и temperature logger.
- задание, отчет, SLA, акт оказанных услуг, тикеты, переписка и подтверждение результата.
- ключевые признаки документа: ответственность перевозчика, лимит ответственности, убытки.
- нормативные ориентиры: ГК РФ, глава 40 (перевозка); Воздушный кодекс РФ; Воздушный кодекс РФ и правила
  воздушных перевозок грузов.

## Типовые пользовательские запросы

| Запрос пользователя | Безопасная реакция ассистента |
|---------------------|-------------------------------|
| Что проверить по рейсу? | Airport pair, flight, booking, AWB, cutoff, terminal status, cargo, пломбы и фото. |
| Кто отвечает за ущерб или просрочку? | Без AWB, terminal timestamps, актов, фото и carrier evidence не решать. |
| Какие факты нужны для «Соглашение об ответственности авиаперевозчика и экспедитора»? | Перечислить недостающие даты, документы, участников, суммы/сроки и ответственных. |
| Можно ли применять автоматически? | Только после проверки ограничений по «Соглашение об ответственности авиаперевозчика и экспедитора»; при риске или неполных фактах нужна ручная проверка. |

## Ответственные роли

| Роль | Зона ответственности |
|------|----------------------|
| Директор по логистике | утверждает применение правила и дату актуальности источника |
| Логист/диспетчер | проверяет airport pair, flight, booking, AWB, cargo, terminal, carrier/GSA и наземное плечо |
| Терминал / склад / наземное плечо | передает для «Соглашение об ответственности авиаперевозчика и экспедитора» booking, AWB, terminal records, CMR/ТТН и GPS только как first/last mile evidence |
| Юрист/Compliance | оценивает вывод об ответственности без AWB, terminal актов, фото и carrier evidence |

## Риски и ограничения

- Нельзя отвечать без проверки: airport origin/destination, booking, AWB/MAWB/HAWB, flight number, cutoff,
  chargeable weight, carrier/GSA, terminal и airline SLA, liability и claims procedure.
- ключевые признаки (ответственность перевозчика, лимит ответственности, убытки) могут быть неверно применены без документа-основания.
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

- ГК РФ, глава 40 (перевозка)
- Воздушный кодекс РФ
- Воздушный кодекс РФ и правила воздушных перевозок грузов

## Критерии качества ответа

- ответ решает именно сценарий «Соглашение об ответственности авиаперевозчика и экспедитора» и не подменяет его общим правилом категории.
- проверено: airport origin/destination, booking, AWB/MAWB/HAWB, flight number, cutoff, chargeable weight,
  carrier/GSA, terminal и airline SLA, liability и claims procedure.
- источники подтверждения: booking, договор air cargo/экспедиции, AWB/MAWB/HAWB, terminal acceptance, screening
  record, ULD/pallet sheet, фото, GPS наземного плеча и service act.
- учтен профильный риск: оплата или вывод об ответственности сделаны без подтверждения рейса, акта, документов и
  отклонений по маршруту.
- ключевые признаки (ответственность перевозчика, лимит ответственности, убытки) использованы только вместе с подтвержденными документами.
- не подставлены airport pair, flight, chargeable weight, пломбы, температура, водитель/ТС наземного плеча,
  CMR/ТТН наземного плеча или акты без air cargo документов.
## Контрольный список

- [ ] запрос сопоставлен с документом «Соглашение об ответственности авиаперевозчика и экспедитора» и типом «соглашение»
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
- [ ] недостающие факты по «Соглашение об ответственности авиаперевозчика и экспедитора» вынесены в уточняющие вопросы

## Порядок пересмотра и актуализации

Владелец документа: Директор по логистике. Плановый пересмотр проводится не реже одного раза в 12 месяцев, а
также при изменении законодательства, организационной структуры, маршрута согласования, ответственных ролей или
используемых шаблонов. Изменения вступают в силу после утверждения владельцем процесса и доведения до
сотрудников или контрагентов, которых затрагивает документ.

## История изменений

| Версия | Дата | Изменение | Автор |
|--------|------|-----------|-------|
| 1.0 | 2026-05-15 | Первичная редакция внутреннего документа | Владелец процесса |

> Применять «Соглашение об ответственности авиаперевозчика и экспедитора» после подтверждения владельцем процесса; спорные и нетиповые кейсы требуют ручной проверки.
