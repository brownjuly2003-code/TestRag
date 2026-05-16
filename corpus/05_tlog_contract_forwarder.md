---
doc_id: tlog_contract_forwarder
title: Договор с air cargo экспедитором (FWC)
category: Transport and logistics legal docs
document_type: договор транспортной экспедиции
department: Logistics
synthetic_demo: false
source_type: internal_controlled
version: "1.0"
effective_date: '2026-05-15'
owner_role: Директор по логистике
related_normative_sources:
- ГК РФ, глава 41 (транспортная экспедиция)
- Воздушный кодекс РФ
keywords:
- экспедитор
- FWC
- долгосрочный договор
- KPI
confidentiality: internal
---

# Договор с air cargo экспедитором (FWC)

## Назначение

Шаблон долгосрочного договора (Forwarder Contract) на организацию перевозок. Документ применяется для контроля air cargo booking, AWB/MAWB/HAWB, terminal milestones и SLA; dangerous goods, lithium batteries, pharma/cold chain, perishables, oversized и valuable cargo уходят на ручную проверку логиста, терминала, carrier/GSA и юристов с привязкой к спецдокументам.

## Область применения

Документ используется в контуре авиагрузовых операций для оформления и проверки booking, AWB/MAWB/HAWB,
terminal acceptance,
screening record, ULD/pallet build-up sheet, актов и фотофиксации; эскалация в юридический отдел происходит при
повреждении, утрате, offload, missed cutoff, security hold, customs hold, temperature excursion, регрессе
страховщика или споре по наземному плечу first/last mile.

## Термины

- **Рабочий экземпляр «Договор с air cargo экспедитором (FWC)»** — версия документа с датой, владельцем процесса, статусом согласования и приложениями, по которой можно принимать внутреннее решение.
- **Основание применения «Договор с air cargo экспедитором (FWC)»** — заявка, приказ, договор, акт, обращение или иной первичный документ, без которого ассистент не должен формировать окончательный вывод.
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
| `forwarder_name` | Наименование экспедитора | `{{forwarder_name}}` |
| `client_name` | Наименование клиента | `{{client_name}}` |
| `contract_term` | Срок договора | `{{contract_term}}` |
| `annual_volume_estimate` | Оценка годового объема | `{{annual_volume_estimate}}` |
| `freight_rates` | Фрахта тарифов | `{{freight_rates}}` |
| `kpi_sla` | KPI/SLA | `{{kpi_sla}}` |
| `exclusivity_clause` | Эксклюзивности условия | `{{exclusivity_clause}}` |

### 3. Подготовка текста

Заполнение ведется только по фактическим данным air cargo booking, авиарейса и подтвержденным перевозочным
документам. Поля, не сверенные с AWB/MAWB/HAWB, terminal log, актом или фотофиксацией, сохраняются как
`{{...}}`; данные авиарейса, airport pair, водитель наземного плеча и cargo не подставляются по предыдущим
рейсам без отдельной проверки.

### 4. Текст шаблона

```
Договор с air cargo экспедитором (FWC)

1. Исходные параметры air cargo операции
- Booking: {{booking_number}}
- AWB/MAWB/HAWB: {{awb_number}} / {{mawb_number}} / {{hawb_number}}
- Аэропорт отправления / назначения: {{airport_origin}} / {{airport_destination}}
- Номер авиарейса и cutoff time: {{flight_number}} / {{cutoff_time}}
- ULD/pallet и chargeable weight: {{uld_or_pallet_id}} / {{chargeable_weight}}
- Terminal handling / security screening: {{terminal_handling_status}} / {{security_screening_status}}
- Номер договора: {{contract_number}}
- Дата договора: {{contract_date}}
- Наименование экспедитора: {{forwarder_name}}
- Наименование клиента: {{client_name}}
- Срок договора: {{contract_term}}
- Оценка годового объема: {{annual_volume_estimate}}
- Фрахта тарифов: {{freight_rates}}
- KPI/SLA: {{kpi_sla}}
- Эксклюзивности условия: {{exclusivity_clause}}

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

### 6. Подписание и хранение

Финальная версия и подтверждающие материалы хранятся в карточке air cargo operation в TMS/WMS/terminal log:
booking, AWB/MAWB/HAWB, cargo manifest, terminal acceptance, screening record, ULD/pallet build-up sheet, акты,
фото, temperature logger, GPS-трек наземного плеча и переписка; доступ получают logistics, terminal/warehouse,
finance, insurance и юристы при споре.


## Рабочие доказательства, сроки и эскалация


- Владелец процесса проверяет, что «Договор с air cargo экспедитором (FWC)» применяется к подтвержденной air
  cargo операции, а не к общей перевозке без booking, AWB/MAWB/HAWB и terminal record.
- Рабочий комплект: forwarder instruction, booking, MAWB/HAWB, consolidation, terminal charges и agent SLA.
  CMR/ТТН, GPS и данные водителя используются только для наземного подвоза или вывоза, если этот участок
  связан с airport pair и рейсом.
- Срок реакции: контроль выполняется до подтверждения экспедиторской услуги клиенту; missed cutoff, failed
  screening, offload, customs/security hold, damage/loss или temperature excursion фиксируются в
  TMS/WMS/terminal log с владельцем и следующим сроком.
- Основания для HOLD/STOP: нет agent instruction, booking confirmation, HAWB split или подтверждения
  charges. Неподтвержденные даты, суммы, персональные данные, пломбы, вес, temperature mode и реквизиты не
  подставляются.
- Маршрут эскалации: forwarder, carrier/GSA, finance, customs и legal; спорный RAG-ответ, проект письма или
  операционное решение блокируются до закрытия доказательств и решения владельца процесса.
## Практический сценарий
- Сценарий: логистика согласует операцию или договор по конкретному air cargo booking, airport pair, авиарейсу,
  терминалу, авиаперевозчику/GSA или экспедитору.
- Проверить: airport origin/destination, booking, AWB/MAWB/HAWB, flight number, cutoff, chargeable weight,
  carrier/GSA, terminal и airline SLA, liability и claims procedure.
- Подтвердить источниками: booking, договор air cargo/экспедиции, AWB/MAWB/HAWB, terminal acceptance, screening
  record, ULD/pallet sheet, фото, GPS наземного плеча и service act.
- Результат: операция закрывается после сверки документов, KPI/SLA и расхождений в реестре претензий.
- Предметная проверка: признаки «экспедитор, FWC, долгосрочный договор, KPI» сверяются с исходными документами и не используются как общий ярлык.

## Air cargo профиль документа

- Для «Договор с air cargo экспедитором (FWC)» air cargo профиль строится вокруг подтвержденного airport
  pair, flight number, booking, AWB/MAWB/HAWB, cutoff time, terminal handling, security screening,
  ULD/pallet build-up и chargeable weight.
- Предметная опора документа: forwarder instruction, booking, MAWB/HAWB, consolidation, terminal charges и
  agent SLA. Эти факты должны быть видны в TMS/WMS/terminal log, акте, фото, переписке carrier/GSA или
  связанном документе.
- First/last mile описывает только подвоз или вывоз до аэропорта: CMR/ТТН, водитель, GPS и данные ТС не
  заменяют AWB, terminal acceptance, screening/build-up records и cargo manifest.
- Special cargo требует ручной проверки для dangerous goods, lithium batteries, pharma/cold chain,
  perishables, oversized и valuable cargo; HOLD наступает, если нет agent instruction, booking confirmation,
  HAWB split или подтверждения charges.
- Эскалация идет через forwarder, carrier/GSA, finance, customs и legal, чтобы документ не превращался в
  общий транспортный шаблон без авиационных доказательств.
## Правила ответа RAG-ассистента

- Использовать документ как источник типа «договор транспортной экспедиции» по теме «Договор с air cargo экспедитором (FWC)» только при фактическом совпадении запроса с предметом документа.
- Перед ответом проверить: airport origin/destination, flight number, booking, AWB/MAWB/HAWB, cutoff time,
  terminal acceptance, security screening, ULD/pallet, gross/chargeable weight, shipper/consignee, carrier/GSA,
  special cargo status; для first/last mile проверить ТС, водителя, terminal pass, CMR/ТТН,
  пломбы, фото, GPS и temperature logger; табель, график, KPI, основание доплаты/премии и расчетный период.
- Если фактов по «Договор с air cargo экспедитором (FWC)» не хватает, вернуть уточняющие вопросы; даты, суммы, доступы и реквизиты оставлять неподтвержденными до проверки.
- Споры, расчеты, санкции, защищенные категории и персональные данные передавать на ручную проверку.

## Доказательства и источники для ответа

- договор air cargo/экспедиции, booking confirmation, AWB/MAWB/HAWB, cargo manifest и terminal acceptance record.
- данные груза: gross/chargeable weight, dimensions, packaging, marking/labels, temperature mode, dangerous
  goods/lithium status, пломбы, ULD/pallet и фото.
- табель, KPI-отчет, приказ о премии, положение об оплате и расчетный лист.
- booking, AWB/MAWB/HAWB, terminal log, screening record, акт, фото, GPS наземного плеча и temperature logger.
- ключевые признаки документа: экспедитор, FWC, долгосрочный договор, KPI.
- нормативные ориентиры: ГК РФ, глава 41 (транспортная экспедиция); Воздушный кодекс РФ.

## Типовые пользовательские запросы

| Запрос пользователя | Безопасная реакция ассистента |
|---------------------|-------------------------------|
| Что проверить по рейсу? | Airport pair, flight, booking, AWB, cutoff, terminal status, cargo, пломбы и фото. |
| Кто отвечает за ущерб или просрочку? | Без AWB, terminal timestamps, актов, фото и carrier evidence не решать. |
| Какие факты нужны для «Договор с air cargo экспедитором (FWC)»? | Перечислить недостающие даты, документы, участников, суммы/сроки и ответственных. |
| Можно ли применять автоматически? | Только после проверки ограничений по «Договор с air cargo экспедитором (FWC)»; при риске или неполных фактах нужна ручная проверка. |

## Ответственные роли

| Роль | Зона ответственности |
|------|----------------------|
| Директор по логистике | утверждает применение правила и дату актуальности источника |
| Логист/диспетчер | проверяет airport pair, flight, booking, AWB, cargo, terminal, carrier/GSA и наземное плечо |
| Терминал / склад / наземное плечо | передает для «Договор с air cargo экспедитором (FWC)» booking, AWB, terminal records, CMR/ТТН и GPS только как first/last mile evidence |
| Юрист/Compliance | оценивает вывод об ответственности без AWB, terminal актов, фото и carrier evidence |

## Риски и ограничения

- Нельзя отвечать без проверки: airport origin/destination, booking, AWB/MAWB/HAWB, flight number, cutoff,
  chargeable weight, carrier/GSA, terminal и airline SLA, liability и claims procedure.
- ключевые признаки (экспедитор, FWC, долгосрочный договор, KPI) могут быть неверно применены без документа-основания.
- вывод об ответственности без AWB/MAWB/HAWB, terminal act, фото, flight status, объяснения
  перевозчика/терминала и доказательства наземного плеча.
- расхождение airport pair, flight number, cargo, gross/chargeable weight, пломбы, ULD/pallet или temperature
  mode между booking, AWB/MAWB/HAWB и terminal records.
- расчет выплаты без табеля, KPI или утвержденного основания.
- несовпадение cargo, airport pair, flight, пломбы, cutoff, terminal SLA или chargeable weight в договоре,
  booking и AWB/MAWB/HAWB.
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

- ГК РФ, глава 41 (транспортная экспедиция)
- Воздушный кодекс РФ

## Критерии качества ответа

- ответ решает именно сценарий «Договор с air cargo экспедитором (FWC)» и не подменяет его общим правилом категории.
- проверено: airport origin/destination, booking, AWB/MAWB/HAWB, flight number, cutoff, chargeable weight,
  carrier/GSA, terminal и airline SLA, liability и claims procedure.
- источники подтверждения: booking, договор air cargo/экспедиции, AWB/MAWB/HAWB, terminal acceptance, screening
  record, ULD/pallet sheet, фото, GPS наземного плеча и service act.
- учтен профильный риск: оплата или вывод об ответственности сделаны без подтверждения рейса, акта, документов и
  отклонений по маршруту.
- ключевые признаки (экспедитор, FWC, долгосрочный договор, KPI) использованы только вместе с подтвержденными документами.
- не подставлены airport pair, flight, chargeable weight, пломбы, температура, водитель/ТС наземного плеча,
  CMR/ТТН наземного плеча или акты без air cargo документов.
## Контрольный список

- [ ] запрос сопоставлен с документом «Договор с air cargo экспедитором (FWC)» и типом «договор транспортной экспедиции»
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
- [ ] недостающие факты по «Договор с air cargo экспедитором (FWC)» вынесены в уточняющие вопросы

## Порядок пересмотра и актуализации

Владелец документа: Директор по логистике. Плановый пересмотр проводится не реже одного раза в 12 месяцев, а
также при изменении законодательства, организационной структуры, маршрута согласования, ответственных ролей или
используемых шаблонов. Изменения вступают в силу после утверждения владельцем процесса и доведения до
сотрудников или контрагентов, которых затрагивает документ.

## История изменений

| Версия | Дата | Изменение | Автор |
|--------|------|-----------|-------|
| 1.0 | 2026-05-15 | Первичная редакция внутреннего документа | Владелец процесса |

> Применять «Договор с air cargo экспедитором (FWC)» после подтверждения владельцем процесса; спорные и нетиповые кейсы требуют ручной проверки.
