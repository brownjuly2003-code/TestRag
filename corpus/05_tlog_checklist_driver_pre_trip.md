---
doc_id: tlog_checklist_driver_pre_trip
title: Чеклист водителя перед подвозом авиагруза к терминалу
category: Transport and logistics legal docs
document_type: чеклист
department: Logistics
synthetic_demo: false
source_type: internal_controlled
version: "1.0"
effective_date: '2026-05-15'
owner_role: Директор по логистике
related_normative_sources:
- Воздушный кодекс РФ
- Приказ Минтранса РФ от 15.10.2020 № 368
- Европейское соглашение ЕСТР
keywords:
- предрейсовый осмотр
- водитель
- алкотест
- тахограф
confidentiality: internal
---

# Чеклист водителя перед подвозом авиагруза к терминалу

## Назначение

Проверочный список медицинского и технического осмотра водителя перед рейсом. Документ применяется для контроля air cargo booking, AWB/MAWB/HAWB, terminal milestones и SLA; dangerous goods, lithium batteries, pharma/cold chain, perishables, oversized и valuable cargo уходят на ручную проверку логиста, терминала, carrier/GSA и юристов с привязкой к спецдокументам.

## Область применения

Логист, диспетчер, склад и авиагрузовой терминал используют документ «Чеклист водителя перед подвозом авиагруза к терминалу» для контроля air cargo booking, приемки на терминале, прохождения security screening, build-up, handover to carrier и recovery at destination. Для dangerous goods, lithium batteries, pharma/cold chain, perishables, oversized и valuable cargo добавляется проверка IATA DGR, SDS/shipper's declaration, температурного профиля, специальных разрешений, security status и valuable cargo instructions.

## Термины

- **Рабочий экземпляр «Чеклист водителя перед подвозом авиагруза к терминалу»** — версия документа с датой, владельцем процесса, статусом согласования и приложениями, по которой можно принимать внутреннее решение.
- **Основание применения «Чеклист водителя перед подвозом авиагруза к терминалу»** — заявка, приказ, договор, акт, обращение или иной первичный документ, без которого ассистент не должен формировать окончательный вывод.
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
| `driver_name` | ФИО водителя | `{{driver_name}}` |
| `inspection_date` | Дата осмотра | `{{inspection_date}}` |
| `medical_exam_result` | Результат медосмотра | `{{medical_exam_result}}` |
| `alcohol_test_result` | Результат алкотеста | `{{alcohol_test_result}}` |
| `sleep_hours` | Часы отдыха перед рейсом | `{{sleep_hours}}` |
| `license_validity` | Срок действия удостоверения | `{{license_validity}}` |
| `tachograph_status` | Статус тахографа | `{{tachograph_status}}` |
| `vehicle_number` | Номер транспортного средства | `{{vehicle_number}}` |

### 3. Подготовка текста

Ответственный сотрудник сверяет каждое поле с первичными источниками рейса: air cargo booking, AWB/MAWB/HAWB,
договором перевозки/экспедиции, terminal acceptance, screening record, ULD/pallet build-up sheet, пломбами,
GPS-треком наземного плеча и температурным листом. Незаполненные значения остаются плейсхолдерами `{{...}}` до
устранения расхождений.

### 4. Текст шаблона

```
Чеклист водителя перед подвозом авиагруза к терминалу

| Контрольная точка | Данные | ОК | Комментарий |
|-------------------|--------|----|-------------|
| ФИО водителя | {{driver_name}} | ☐ | |
| Дата осмотра | {{inspection_date}} | ☐ | |
| Результат медосмотра | {{medical_exam_result}} | ☐ | |
| Результат алкотеста | {{alcohol_test_result}} | ☐ | |
| Часы отдыха перед рейсом | {{sleep_hours}} | ☐ | |
| Срок действия удостоверения | {{license_validity}} | ☐ | |
| Статус тахографа | {{tachograph_status}} | ☐ | |
| Номер транспортного средства | {{vehicle_number}} | ☐ | |
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


- Владелец процесса проверяет, что «Чеклист водителя перед подвозом авиагруза к терминалу» применяется к
  подтвержденной air cargo операции, а не к общей перевозке без booking, AWB/MAWB/HAWB и terminal record.
- Рабочий комплект: операционный комплект для «Чеклист водителя перед подвозом авиагруза к терминалу»:
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

- GO: водитель выходит на first/last mile смену, если медосмотр, путевой лист, airport pass, маршрут к
  терминалу, AWB/booking, CMR/ТТН автоплеча, GPS, пломбы и инструкции по special cargo подтверждены.
- HOLD: отсутствует пропуск, медосмотр, маршрутный лист, подтверждение terminal slot, связь с AWB/booking
  или отметка о состоянии пломб/температуры.
- STOP: водитель не допущен в controlled zone, есть алкоголь/медицинское ограничение, нарушение security,
  неисправность ТС, опасный груз без инструктажа или потеря GPS до терминала.
## Практический сценарий
- Сценарий: диспетчер или механик применяет «Чеклист водителя перед подвозом авиагруза к терминалу» перед подвозом/вывозом авиагруза на наземном плече first/last mile.
- Проверить: водителя и ТС наземного аэропортового плеча first/last mile, terminal pass, CMR/ТТН
  наземного плеча, пломбы,
  GPS status, temperature logger, tender/recovery time slot и working time limits.
- Подтвердить источниками: CMR/ТТН наземного плеча, terminal pass, чек-лист ТС, GPS track, temperature
  logger, medical/shift check, repair request и defect фото.
- Результат: выпуск рейса подтверждается чек-листом; критичные отклонения передаются механику и руководителю логистики.
- Предметная проверка: признаки «водитель наземного плеча first/last mile, terminal pass, alcohol test, tachograph» сверяются с исходными документами и не используются как общий ярлык.

## Air cargo профиль документа
- Документ относится к наземному плечу: проверяются водитель, ТС, terminal pass, CMR/ТТН, GPS, пломбы,
  температурное оборудование и readiness к cutoff, а не условия авиаперевозки по AWB.
- AWB/booking, airport pair и flight number нужны как контекст рейса, чтобы не выпустить машину к неверному
  терминалу, времени tender или грузу.
- Dangerous goods, lithium, pharma/cold chain и security escort требуют подтверждения допуска водителя/ТС до
  выезда, иначе операция остается в HOLD.
## Правила ответа RAG-ассистента

- Использовать документ как источник типа «чеклист» по теме «Чеклист водителя перед подвозом авиагруза к терминалу» только при фактическом совпадении запроса с предметом документа.
- Перед ответом проверить: airport origin/destination, flight number, booking, AWB/MAWB/HAWB, cutoff time,
  terminal acceptance, security screening, ULD/pallet, gross/chargeable weight, shipper/consignee, carrier/GSA,
  special cargo status; для first/last mile проверить ТС, водителя, terminal pass, CMR/ТТН,
  пломбы, фото, GPS и temperature logger.
- Если фактов по «Чеклист водителя перед подвозом авиагруза к терминалу» не хватает, вернуть уточняющие вопросы; даты, суммы, доступы и реквизиты оставлять неподтвержденными до проверки.
- Споры, расчеты, санкции, защищенные категории и персональные данные передавать на ручную проверку.

## Доказательства и источники для ответа

- договор air cargo/экспедиции, booking confirmation, AWB/MAWB/HAWB, cargo manifest и terminal acceptance record.
- данные груза: gross/chargeable weight, dimensions, packaging, marking/labels, temperature mode, dangerous
  goods/lithium status, пломбы, ULD/pallet и фото.
- ключевые признаки документа: водитель наземного плеча first/last mile, terminal pass, alcohol test, tachograph.
- нормативные ориентиры: Воздушный кодекс РФ; Приказ Минтранса РФ от 15.10.2020 № 368; Европейское соглашение ЕСТР.

## Типовые пользовательские запросы

| Запрос пользователя | Безопасная реакция ассистента |
|---------------------|-------------------------------|
| Что проверить по рейсу? | Airport pair, flight, booking, AWB, cutoff, terminal status, cargo, пломбы и фото. |
| Кто отвечает за ущерб или просрочку? | Без AWB, terminal timestamps, актов, фото и carrier evidence не решать. |
| Какие факты нужны для «Чеклист водителя перед подвозом авиагруза к терминалу»? | Перечислить недостающие даты, документы, участников, суммы/сроки и ответственных. |
| Можно ли применять автоматически? | Только после проверки ограничений по «Чеклист водителя перед подвозом авиагруза к терминалу»; при риске или неполных фактах нужна ручная проверка. |

## Ответственные роли

| Роль | Зона ответственности |
|------|----------------------|
| Директор по логистике | утверждает применение правила и дату актуальности источника |
| Диспетчер автоплеча | проверяет водителя, ТС, terminal pass, маршрут, GPS, пломбы и готовность к cutoff |
| Водитель | подтверждает предрейсовый осмотр, документы, связь, температурное оборудование и запреты по грузу |
| Терминал / склад | сверяет pass, слот, место handover и требования security screening |
| Юрист/Compliance | подключается при споре, ПДн водителя, нарушении режима доступа или претензии |

## Риски и ограничения

- Нельзя отвечать без проверки: водителя и ТС наземного аэропортового плеча first/last mile, terminal pass, CMR/ТТН
  наземного плеча, пломбы, GPS status, temperature logger, tender/recovery time slot и working time limits.
- ключевые признаки (водитель наземного плеча first/last mile, terminal pass, alcohol test, tachograph) могут быть неверно применены без документа-основания.
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
- Приказ Минтранса РФ от 15.10.2020 № 368
- Европейское соглашение ЕСТР

## Критерии качества ответа

- ответ решает именно сценарий «Чеклист водителя перед подвозом авиагруза к терминалу» и не подменяет его общим правилом категории.
- проверено: водителя и ТС наземного аэропортового плеча first/last mile, terminal pass, CMR/ТТН
  наземного плеча, пломбы,
  GPS status, temperature logger, tender/recovery time slot и working time limits.
- источники подтверждения: CMR/ТТН наземного плеча, terminal pass, чек-лист ТС, GPS track, temperature
  logger, medical/shift check, repair request и defect фото.
- учтен профильный риск: выезд на наземное плечо first/last mile выполнен без terminal pass,
  проверки ТС/водителя, seal, GPS,
  temperature logger или defect closure.
- ключевые признаки (водитель наземного плеча first/last mile, terminal pass, alcohol test, tachograph) использованы только вместе с подтвержденными документами.
- не подставлены airport pair, flight, chargeable weight, пломбы, температура, водитель/ТС наземного плеча,
  CMR/ТТН наземного плеча или акты без air cargo документов.
## Контрольный список

- [ ] запрос сопоставлен с документом «Чеклист водителя перед подвозом авиагруза к терминалу» и типом «чеклист»
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
- [ ] недостающие факты по «Чеклист водителя перед подвозом авиагруза к терминалу» вынесены в уточняющие вопросы

## Порядок пересмотра и актуализации

Владелец документа: Директор по логистике. Плановый пересмотр проводится не реже одного раза в 12 месяцев, а
также при изменении законодательства, организационной структуры, маршрута согласования, ответственных ролей или
используемых шаблонов. Изменения вступают в силу после утверждения владельцем процесса и доведения до
сотрудников или контрагентов, которых затрагивает документ.

## История изменений

| Версия | Дата | Изменение | Автор |
|--------|------|-----------|-------|
| 1.0 | 2026-05-15 | Первичная редакция внутреннего документа | Владелец процесса |

> Применять «Чеклист водителя перед подвозом авиагруза к терминалу» после подтверждения владельцем процесса; спорные и нетиповые кейсы требуют ручной проверки.
