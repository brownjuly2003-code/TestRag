---
doc_id: tlog_checklist_claims_road
title: Чеклист претензионной работы по авиагрузу и наземному плечу
category: Transport and logistics legal docs
document_type: чеклист
department: Logistics
synthetic_demo: false
source_type: internal_controlled
version: "1.0"
effective_date: '2026-05-15'
owner_role: Директор по логистике
related_normative_sources:
- ГК РФ, глава 40 (перевозка)
- Воздушный кодекс РФ
- КоАП РФ (административная ответственность)
keywords:
- ДТП
- претензия
- страховка
- повреждение
confidentiality: internal
---

# Чеклист претензионной работы по авиагрузу и наземному плечу

## Назначение

Проверочный список действий при ДТП, повреждении груза или транспортного средства. Логист или диспетчер ООО «Северный Контур» применяет документ при выпуске рейса, приёмке груза или закрытии операции; расхождения по маршруту, грузу, весу или пломбам фиксируются актом до передачи груза следующему участнику цепочки.

## Область применения

Документ используется в контуре авиагрузовых операций для оформления и проверки booking, AWB/MAWB/HAWB,
terminal acceptance,
screening record, ULD/pallet build-up sheet, актов и фотофиксации; эскалация в юридический отдел происходит при
повреждении, утрате, offload, missed cutoff, security hold, customs hold, temperature excursion, регрессе
страховщика или споре по наземному плечу first/last mile.

## Термины

- **Рабочий экземпляр «Чеклист претензионной работы по авиагрузу и наземному плечу»** — версия документа с датой, владельцем процесса, статусом согласования и приложениями, по которой можно принимать внутреннее решение.
- **Основание применения «Чеклист претензионной работы по авиагрузу и наземному плечу»** — заявка, приказ, договор, акт, обращение или иной первичный документ, без которого ассистент не должен формировать окончательный вывод.
- **Контрольная точка** — проверяемое действие до cutoff, при terminal acceptance, security screening,
  ULD/pallet build-up, handover to airline, arrival/recovery или наземного плеча first/last mile.
- **Фотофиксация** — снимки упаковки, маркировки, labels, пломб, ULD/pallet, temperature logger, terminal
  damage, документов и пломбы ТС наземного плеча с датой, временем, airport/terminal и flight/booking reference.
- **Запрет выпуска/приемки** — основание не tenderить груз в терминал или не выпускать наземного плеча: нет
  AWB/booking, missed cutoff, failed screening, неверная DGR/lithium/cold-chain маркировка, повреждение
  упаковки, несоответствие chargeable weight, отсутствие пломбы/GPS/temperature logger или terminal rejection.

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
| `incident_date` | Дата инцидента | `{{incident_date}}` |
| `incident_location` | Инцидента места | `{{incident_location}}` |
| `driver_name` | ФИО водителя | `{{driver_name}}` |
| `vehicle_number` | Номер транспортного средства | `{{vehicle_number}}` |
| `police_report_number` | Номер полицейского протокола | `{{police_report_number}}` |
| `insurance_notification_date` | Дата страхования уведомления | `{{insurance_notification_date}}` |
| `damage_photos` | Фотографии повреждений | `{{damage_photos}}` |
| `witness_contacts` | Контакты свидетелей | `{{witness_contacts}}` |
| `cargo_condition` | Груза состояния | `{{cargo_condition}}` |

### 3. Подготовка текста

Логист или диспетчер заполняет только подтвержденные поля по booking, AWB/MAWB/HAWB, terminal acceptance,
screening record, CMR/ТТН наземного плеча и фотофиксации. Плейсхолдеры `{{...}}` остаются для несверенных данных
груза, airport pair, пломб, ULD/pallet или ТС наземного плеча; подстановка по аналогии не допускается.

### 4. Текст шаблона

```
Чеклист претензионной работы по авиагрузу и наземному плечу

| Контрольная точка | Данные | ОК | Комментарий |
|-------------------|--------|----|-------------|
| Дата инцидента | {{incident_date}} | ☐ | |
| Инцидента места | {{incident_location}} | ☐ | |
| ФИО водителя | {{driver_name}} | ☐ | |
| Номер транспортного средства | {{vehicle_number}} | ☐ | |
| Номер полицейского протокола | {{police_report_number}} | ☐ | |
| Дата страхования уведомления | {{insurance_notification_date}} | ☐ | |
| Фотографии повреждений | {{damage_photos}} | ☐ | |
| Контакты свидетелей | {{witness_contacts}} | ☐ | |
| Груза состояния | {{cargo_condition}} | ☐ | |
| Проверка маршрута | {{route_check}} | ☐ | |
| Проверка ограничений | {{restriction_check}} | ☐ | |
| Проверка доказательств | {{evidence_check}} | ☐ | |

Итог: {{approval_status}}
Ответственный: {{responsible_officer}}
Дата проверки: {{review_date}}
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


- Владелец процесса проверяет, что «Чеклист претензионной работы по авиагрузу и наземному плечу» применяется
  к подтвержденной air cargo операции, а не к общей перевозке без booking, AWB/MAWB/HAWB и terminal record.
- Рабочий комплект: операционный комплект для «Чеклист претензионной работы по авиагрузу и наземному плечу»:
  booking, AWB/MAWB/HAWB, terminal record и доказательства отклонений. CMR/ТТН, GPS и данные водителя
  используются только для наземного подвоза или вывоза, если этот участок связан с airport pair и рейсом.
- Срок реакции: контроль выполняется до закрытия air cargo операции; missed cutoff, failed screening,
  offload, customs/security hold, damage/loss или temperature excursion фиксируются в TMS/WMS/terminal log с
  владельцем и следующим сроком.
- Основания для HOLD/STOP: нет booking/AWB, terminal record, evidence pack или владельца отклонения.
  Неподтвержденные даты, суммы, персональные данные, пломбы, вес, temperature mode и реквизиты не
  подставляются.
- Маршрут эскалации: logistics, terminal, carrier/GSA, finance, compliance и legal; спорный RAG-ответ,
  проект письма или операционное решение блокируются до закрытия доказательств и решения владельца процесса.
## Stop/go критерии

- GO: claim по road first/last mile можно готовить, если CMR/ТТН, GPS, пломбы, фото, акт, terminal
  timestamp, AWB/booking и cutoff рейса подтверждают связь автоплеча с авиагрузом.
- HOLD: не хватает GPS, акта, фото, данных пломб, terminal pass, времени прибытия или договора с
  перевозчиком; ответ ограничивается запросом доказательств.
- STOP: позиция признает вину/долг без Legal, CMR/ТТН подменяет AWB, спор затрагивает dangerous
  goods/customs/security или сумма требования не подтверждена расчетом.
## Практический сценарий
- Сценарий: логистика согласует операцию или договор по конкретному air cargo booking, airport pair, авиарейсу,
  терминалу, авиаперевозчику/GSA или экспедитору.
- Проверить: airport origin/destination, booking, AWB/MAWB/HAWB, flight number, cutoff, chargeable weight,
  carrier/GSA, terminal и airline SLA, liability и claims procedure.
- Подтвердить источниками: booking, договор air cargo/экспедиции, AWB/MAWB/HAWB, terminal acceptance, screening
  record, ULD/pallet sheet, фото, GPS наземного плеча и service act.
- Результат: операция закрывается после сверки документов, KPI/SLA и расхождений в реестре претензий.
- Предметная проверка: признаки «ДТП, претензия, страховка, повреждение» сверяются с исходными документами и не используются как общий ярлык.

## Air cargo профиль документа
- Для претензии разделяются факты воздушной перевозки и first/last mile: AWB, flight status, terminal
  timestamps
  и carrier evidence сопоставляются с CMR/ТТН, GPS, пломбами и актом водителя.
- Наземное плечо подтверждает только pickup/delivery, время прибытия, целостность пломб и состояние
  упаковки;
  оно не заменяет cargo irregularity report, terminal damage note или carrier response.
- Special cargo претензии требуют отдельного temperature log, DG/lithium/cold-chain evidence, фото
  маркировки и
  решения insurance/Legal до ответа клиенту.
## Правила ответа RAG-ассистента

- Использовать документ как источник типа «чеклист» по теме «Чеклист претензионной работы по авиагрузу и наземному плечу» только при фактическом совпадении запроса с предметом документа.
- Перед ответом проверить: airport origin/destination, flight number, booking, AWB/MAWB/HAWB, cutoff time,
  terminal acceptance, security screening, ULD/pallet, gross/chargeable weight, shipper/consignee, carrier/GSA,
  special cargo status; для first/last mile проверить ТС, водителя, terminal pass, CMR/ТТН,
  пломбы, фото, GPS и temperature logger.
- Если фактов по «Чеклист претензионной работы по авиагрузу и наземному плечу» не хватает, вернуть уточняющие вопросы; даты, суммы, доступы и реквизиты оставлять неподтвержденными до проверки.
- Споры, расчеты, санкции, защищенные категории и персональные данные передавать на ручную проверку.

## Доказательства и источники для ответа

- договор air cargo/экспедиции, booking confirmation, AWB/MAWB/HAWB, cargo manifest и terminal acceptance record.
- данные груза: gross/chargeable weight, dimensions, packaging, marking/labels, temperature mode, dangerous
  goods/lithium status, пломбы, ULD/pallet и фото.
- booking, AWB/MAWB/HAWB, terminal log, screening record, акт, фото, GPS наземного плеча и temperature logger.
- акт, фото, накладная, счет, переписка, расчет неустойки/убытков и доказательство отправки.
- ключевые признаки документа: ДТП, претензия, страховка, повреждение.
- нормативные ориентиры: ГК РФ, глава 40 (перевозка); Воздушный кодекс РФ; КоАП РФ (административная ответственность).

## Типовые пользовательские запросы

| Запрос пользователя | Безопасная реакция ассистента |
|---------------------|-------------------------------|
| Что проверить по рейсу? | Airport pair, flight, booking, AWB, cutoff, terminal status, cargo, пломбы и фото. |
| Кто отвечает за ущерб или просрочку? | Без AWB, terminal timestamps, актов, фото и carrier evidence не решать. |
| Какие факты нужны для «Чеклист претензионной работы по авиагрузу и наземному плечу»? | Перечислить недостающие даты, документы, участников, суммы/сроки и ответственных. |
| Можно ли применять автоматически? | Только после проверки ограничений по «Чеклист претензионной работы по авиагрузу и наземному плечу»; при риске или неполных фактах нужна ручная проверка. |

## Ответственные роли

| Роль | Зона ответственности |
|------|----------------------|
| Директор по логистике | утверждает применение правила и дату актуальности источника |
| Логист/диспетчер | собирает timeline по AWB, flight, cutoff, terminal handover и first/last mile |
| Claims owner | ведет сумму требования, срок ответа, доказательства вручения и позицию к перевозчику/терминалу |
| Владелец наземного плеча | передает CMR/ТТН, GPS, пломбы, фото и объяснения водителя |
| Юрист/Compliance | проверяет признание ответственности, санкции, ПДн и допустимый объем раскрытия доказательств |

## Риски и ограничения

- Нельзя отвечать без проверки: airport origin/destination, booking, AWB/MAWB/HAWB, flight number, cutoff,
  chargeable weight, carrier/GSA, terminal и airline SLA, liability и claims procedure.
- ключевые признаки (ДТП, претензия, страховка, повреждение) могут быть неверно применены без документа-основания.
- вывод об ответственности без AWB/MAWB/HAWB, terminal act, фото, flight status, объяснения
  перевозчика/терминала и доказательства наземного плеча.
- расхождение airport pair, flight number, cargo, gross/chargeable weight, пломбы, ULD/pallet или temperature
  mode между booking, AWB/MAWB/HAWB и terminal records.
- несовпадение cargo, airport pair, flight, пломбы, cutoff, terminal SLA или chargeable weight в договоре,
  booking и AWB/MAWB/HAWB.
- позиция содержит признание вины, долга или отказ от возражений.
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
- КоАП РФ (административная ответственность)

## Критерии качества ответа

- ответ решает именно сценарий «Чеклист претензионной работы по авиагрузу и наземному плечу» и не подменяет его общим правилом категории.
- проверено: airport origin/destination, booking, AWB/MAWB/HAWB, flight number, cutoff, chargeable weight,
  carrier/GSA, terminal и airline SLA, liability и claims procedure.
- источники подтверждения: booking, договор air cargo/экспедиции, AWB/MAWB/HAWB, terminal acceptance, screening
  record, ULD/pallet sheet, фото, GPS наземного плеча и service act.
- учтен профильный риск: оплата или вывод об ответственности сделаны без подтверждения рейса, акта, документов и
  отклонений по маршруту.
- ключевые признаки (ДТП, претензия, страховка, повреждение) использованы только вместе с подтвержденными документами.
- не подставлены airport pair, flight, chargeable weight, пломбы, температура, водитель/ТС наземного плеча,
  CMR/ТТН наземного плеча или акты без air cargo документов.
## Контрольный список

- [ ] запрос сопоставлен с документом «Чеклист претензионной работы по авиагрузу и наземному плечу» и типом «чеклист»
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
- [ ] недостающие факты по «Чеклист претензионной работы по авиагрузу и наземному плечу» вынесены в уточняющие вопросы

## Порядок пересмотра и актуализации

Владелец документа: Директор по логистике. Плановый пересмотр проводится не реже одного раза в 12 месяцев, а
также при изменении законодательства, организационной структуры, маршрута согласования, ответственных ролей или
используемых шаблонов. Изменения вступают в силу после утверждения владельцем процесса и доведения до
сотрудников или контрагентов, которых затрагивает документ.

## История изменений

| Версия | Дата | Изменение | Автор |
|--------|------|-----------|-------|
| 1.0 | 2026-05-15 | Первичная редакция внутреннего документа | Владелец процесса |

> Применять «Чеклист претензионной работы по авиагрузу и наземному плечу» после подтверждения владельцем процесса; спорные и нетиповые кейсы требуют ручной проверки.
