---
doc_id: tlog_checklist_cargo_acceptance
title: Чеклист приемки авиагруза к перевозке
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
- Воздушный кодекс РФ и правила воздушных перевозок грузов
keywords:
- приемка груза
- чеклист
- упаковка
- пломба
confidentiality: internal
---

# Чеклист приемки авиагруза к перевозке

## Назначение

Проверочный список для приемки груза от грузоотправителя. Сотрудник логистического контура сверяет air cargo booking, AWB/MAWB/HAWB, аэропорт отправления и назначения, номер рейса, cutoff time, terminal handling, security screening, ULD/pallet build-up, chargeable weight, пломбы, фотофиксацию и GPS/температурные данные наземного плеча; решение о допуске груза к авиарейсу принимается только после устранения расхождений и подтверждения терминала или авиаперевозчика.

## Область применения

Документ используется в контуре авиагрузовых операций для оформления и проверки booking, AWB/MAWB/HAWB,
terminal acceptance,
screening record, ULD/pallet build-up sheet, актов и фотофиксации; эскалация в юридический отдел происходит при
повреждении, утрате, offload, missed cutoff, security hold, customs hold, temperature excursion, регрессе
страховщика или споре по наземному плечу first/last mile.

## Термины

- **Рабочий экземпляр «Чеклист приемки авиагруза к перевозке»** — версия документа с датой, владельцем процесса, статусом согласования и приложениями, по которой можно принимать внутреннее решение.
- **Основание применения «Чеклист приемки авиагруза к перевозке»** — заявка, приказ, договор, акт, обращение или иной первичный документ, без которого ассистент не должен формировать окончательный вывод.
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
| `waybill_number` | Номер накладной | `{{waybill_number}}` |
| `cargo_description` | Описание груза | `{{cargo_description}}` |
| `places_count` | Количество мест | `{{places_count}}` |
| `weight` | Вес | `{{weight}}` |
| `packaging_condition` | Состояние упаковки | `{{packaging_condition}}` |
| `seal_number` | Номер пломбы | `{{seal_number}}` |
| `marking_compliance` | Соответствие маркировки | `{{marking_compliance}}` |
| `temperature_check` | Проверка температуры | `{{temperature_check}}` |
| `damage_notes` | Замечания о повреждениях | `{{damage_notes}}` |

### 3. Подготовка текста

Ответственный сотрудник сверяет каждое поле с первичными источниками рейса: air cargo booking, AWB/MAWB/HAWB,
договором перевозки/экспедиции, terminal acceptance, screening record, ULD/pallet build-up sheet, пломбами,
GPS-треком наземного плеча и температурным листом. Незаполненные значения остаются плейсхолдерами `{{...}}` до
устранения расхождений.

### 4. Текст шаблона

```
Чеклист приемки авиагруза к перевозке

| Контрольная точка | Данные | ОК | Комментарий |
|-------------------|--------|----|-------------|
| Номер накладной | {{waybill_number}} | ☐ | |
| Описание груза | {{cargo_description}} | ☐ | |
| Количество мест | {{places_count}} | ☐ | |
| Вес | {{weight}} | ☐ | |
| Состояние упаковки | {{packaging_condition}} | ☐ | |
| Номер пломбы | {{seal_number}} | ☐ | |
| Соответствие маркировки | {{marking_compliance}} | ☐ | |
| Проверка температуры | {{temperature_check}} | ☐ | |
| Замечания о повреждениях | {{damage_notes}} | ☐ | |
| Проверка маршрута | {{route_check}} | ☐ | |
| Проверка ограничений | {{restriction_check}} | ☐ | |
| Проверка доказательств | {{evidence_check}} | ☐ | |

Итог: {{approval_status}}
Ответственный: {{responsible_officer}}
Дата проверки: {{review_date}}
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

- Владелец процесса сверяет дату события, действующую редакцию, подразделение/контрагента и подтверждающий
  документ; неподтвержденные даты, суммы, персональные данные и реквизиты не подставляются.
- Рабочий комплект: air cargo booking, AWB/MAWB/HAWB, airport origin/destination, flight number, cutoff
  time,
  terminal acceptance, security screening record, ULD/pallet build-up sheet, gross/chargeable weight, cargo
  фото, пломбы, temperature logger, insurance certificate, customs/security notes, а также CMR/ТТН, GPS и
  документы водителя/ТС только для наземного плеча first/last mile; отсутствие сведений о booking, AWB/MAWB/HAWB,
  airport pair, flight, cutoff, cargo, special cargo status, terminal handling, screening, ULD/pallet,
  chargeable weight, пломбы, temperature mode или подтверждения наземного плеча является основанием остановить
  финальное решение или проект.
- Срок реакции: чеклист закрывается до terminal acceptance; расхождения по местам, весу, пломбам, упаковке,
  ULD/pallet, temperature logger или screening фиксируются в TMS/WMS/terminal log в течение 30 минут после
  обнаружения.
- Основания для отказа или ручной проверки: dangerous goods, lithium batteries, pharma/cold chain,
  perishables,
  oversized, valuable cargo, damaged packaging, terminal rejection, missed cutoff, failed screening, offload,
  customs/security hold, temperature excursion, chargeable weight mismatch или потеря GPS на наземном плече;
  ассистент останавливается на уточняющих вопросах до документального подтверждения.
- Маршрут эскалации: приемщик терминала, air cargo dispatcher, warehouse/WMS owner, terminal supervisor,
  security screening contact, carrier/GSA и claims; водитель подключается только по фактам подвоза/вывоза
  first/last mile.

## Stop/go критерии

- GO: груз принят к air cargo операции, если booking, AWB/MAWB/HAWB, airport pair, flight number, cutoff,
  terminal slot, screening requirement, gross/chargeable weight, ULD/pallet plan и special cargo status
  подтверждены в TMS/WMS/terminal log.
- HOLD: есть расхождение по местам, весу, пломбам, упаковке, temperature mode, airport pair, flight status,
  terminal slot или данным наземного подвоза; приемка ждет уточнения владельца процесса.
- STOP: нет AWB/booking, failed screening, terminal rejection, повреждение упаковки, неверная
  DGR/lithium/cold-chain маркировка, неподтвержденный ULD/pallet build-up, потеря пломбы или отсутствие
  temperature logger для pharma/perishables.
## Практический сценарий
- Сценарий: логист оформляет перевозочные документы по «Чеклист приемки авиагруза к перевозке» до terminal acceptance, cutoff time и выпуском на рейс.
- Проверить: airport origin/destination, flight number, AWB/MAWB/HAWB, booking, places, gross/chargeable weight,
  ULD/pallet, пломбы, shipper, consignee, carrier/GSA, terminal acceptance и акты.
- Подтвердить источниками: AWB/MAWB/HAWB, booking, terminal acceptance, cargo irregularity/damage report, фото,
  пломбы, ULD/pallet record, GPS наземного плеча и подписи.
- Результат: расхождения фиксируются до передачи груза следующему участнику и до выставления претензии.
- Предметная проверка: признаки «приемка груза, чеклист, упаковка, пломба» сверяются с исходными документами и не используются как общий ярлык.

## Air cargo профиль документа
- Чеклист приемки привязан к фактическому handover: booking, AWB/MAWB/HAWB, terminal slot, состояние
  упаковки,
  пломбы, places, gross/chargeable weight и фото до передачи в терминал.
- Наземное плечо first/last mile подтверждает только доставку до терминала: CMR/ТТН, GPS и данные водителя
  сверяются с terminal acceptance, но не заменяют AWB и screening record.
- Special cargo не принимается по общему чек-листу без отметок dangerous goods/lithium/cold chain,
  маркировки,
  temperature logger и разрешения терминала или carrier/GSA.
## Правила ответа RAG-ассистента

- Использовать документ как источник типа «чеклист» по теме «Чеклист приемки авиагруза к перевозке» только при фактическом совпадении запроса с предметом документа.
- Перед ответом проверить: airport origin/destination, flight number, booking, AWB/MAWB/HAWB, cutoff time,
  terminal acceptance, security screening, ULD/pallet, gross/chargeable weight, shipper/consignee, carrier/GSA,
  special cargo status; для first/last mile проверить ТС, водителя, terminal pass, CMR/ТТН,
  пломбы, фото, GPS и temperature logger.
- Если фактов по «Чеклист приемки авиагруза к перевозке» не хватает, вернуть уточняющие вопросы; даты, суммы, доступы и реквизиты оставлять неподтвержденными до проверки.
- Споры, расчеты, санкции, защищенные категории и персональные данные передавать на ручную проверку.

## Доказательства и источники для ответа

- договор air cargo/экспедиции, booking confirmation, AWB/MAWB/HAWB, cargo manifest и terminal acceptance record.
- данные груза: gross/chargeable weight, dimensions, packaging, marking/labels, temperature mode, dangerous
  goods/lithium status, пломбы, ULD/pallet и фото.
- booking, AWB/MAWB/HAWB, terminal log, screening record, акт, фото, GPS наземного плеча и temperature logger.
- ключевые признаки документа: приемка груза, чеклист, упаковка, пломба.
- нормативные ориентиры: ГК РФ, глава 40 (перевозка); Воздушный кодекс РФ; Воздушный кодекс РФ и правила
  воздушных перевозок грузов.

## Типовые пользовательские запросы

| Запрос пользователя | Безопасная реакция ассистента |
|---------------------|-------------------------------|
| Что проверить по рейсу? | Airport pair, flight, booking, AWB, cutoff, terminal status, cargo, пломбы и фото. |
| Кто отвечает за ущерб или просрочку? | Без AWB, terminal timestamps, актов, фото и carrier evidence не решать. |
| Какие факты нужны для «Чеклист приемки авиагруза к перевозке»? | Перечислить недостающие даты, документы, участников, суммы/сроки и ответственных. |
| Можно ли применять автоматически? | Только после проверки ограничений по «Чеклист приемки авиагруза к перевозке»; при риске или неполных фактах нужна ручная проверка. |

## Ответственные роли

| Роль | Зона ответственности |
|------|----------------------|
| Директор по логистике | утверждает применение правила и дату актуальности источника |
| Логист/диспетчер | сверяет booking, AWB, cutoff, carrier/GSA и готовность к terminal tender |
| Приемщик терминала / склад | фиксирует места, вес, упаковку, пломбы, damage notes, screening и terminal timestamps |
| Владелец наземного плеча | передает CMR/ТТН, GPS, фото прибытия и данные водителя только для first/last mile |
| Юрист/Compliance | подключается при повреждении, утрате, спорной ответственности, sanctions/DG/PDP или отказе терминала |

## Риски и ограничения

- Нельзя отвечать без проверки: airport origin/destination, flight number, AWB/MAWB/HAWB, booking, places,
  gross/chargeable weight, ULD/pallet, пломбы, shipper, consignee, carrier/GSA, terminal acceptance и акты.
- ключевые признаки (приемка груза, чеклист, упаковка, пломба) могут быть неверно применены без документа-основания.
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

- ГК РФ, глава 40 (перевозка)
- Воздушный кодекс РФ
- Воздушный кодекс РФ и правила воздушных перевозок грузов

## Критерии качества ответа

- ответ решает именно сценарий «Чеклист приемки авиагруза к перевозке» и не подменяет его общим правилом категории.
- проверено: airport origin/destination, flight number, AWB/MAWB/HAWB, booking, places, gross/chargeable weight,
  ULD/pallet, пломбы, shipper, consignee, carrier/GSA, terminal acceptance и акты.
- источники подтверждения: AWB/MAWB/HAWB, booking, terminal acceptance, cargo irregularity/damage report, фото,
  пломбы, ULD/pallet record, GPS наземного плеча и подписи.
- учтен профильный риск: данные груза, airport pair, flight, chargeable weight, пломбы или ULD/pallet расходятся
  между booking, AWB/MAWB/HAWB, terminal log и актом.
- ключевые признаки (приемка груза, чеклист, упаковка, пломба) использованы только вместе с подтвержденными документами.
- не подставлены airport pair, flight, chargeable weight, пломбы, температура, водитель/ТС наземного плеча,
  CMR/ТТН наземного плеча или акты без air cargo документов.
## Контрольный список

- [ ] запрос сопоставлен с документом «Чеклист приемки авиагруза к перевозке» и типом «чеклист»
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
- [ ] недостающие факты по «Чеклист приемки авиагруза к перевозке» вынесены в уточняющие вопросы

## Порядок пересмотра и актуализации

Владелец документа: Директор по логистике. Плановый пересмотр проводится не реже одного раза в 12 месяцев, а
также при изменении законодательства, организационной структуры, маршрута согласования, ответственных ролей или
используемых шаблонов. Изменения вступают в силу после утверждения владельцем процесса и доведения до
сотрудников или контрагентов, которых затрагивает документ.

## История изменений

| Версия | Дата | Изменение | Автор |
|--------|------|-----------|-------|
| 1.0 | 2026-05-15 | Первичная редакция внутреннего документа | Владелец процесса |

> Применять «Чеклист приемки авиагруза к перевозке» после подтверждения владельцем процесса; спорные и нетиповые кейсы требуют ручной проверки.
