---
doc_id: tlog_checklist_vehicle_inspection
title: Чеклист осмотра транспорта для подвоза авиагруза к терминалу
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
- Правила технической эксплуатации
keywords:
- техосмотр
- чеклист
- автомобиль
- безопасность
confidentiality: internal
---

# Чеклист осмотра транспорта для подвоза авиагруза к терминалу

## Назначение

Проверочный список ежедневного/еженедельного техосмотра автомобиля. Сотрудник логистического контура сверяет air cargo booking, AWB/MAWB/HAWB, аэропорт отправления и назначения, номер рейса, cutoff time, terminal handling, security screening, ULD/pallet build-up, chargeable weight, пломбы, фотофиксацию и GPS/температурные данные наземного плеча; решение о допуске груза к авиарейсу принимается только после устранения расхождений и подтверждения терминала или авиаперевозчика.

## Область применения

Документ используется в контуре авиагрузовых операций для оформления и проверки booking, AWB/MAWB/HAWB,
terminal acceptance,
screening record, ULD/pallet build-up sheet, актов и фотофиксации; эскалация в юридический отдел происходит при
повреждении, утрате, offload, missed cutoff, security hold, customs hold, temperature excursion, регрессе
страховщика или споре по наземному плечу first/last mile.

## Термины

- **Рабочий экземпляр «Чеклист осмотра транспорта для подвоза авиагруза к терминалу»** — версия документа с датой, владельцем процесса, статусом согласования и приложениями, по которой можно принимать внутреннее решение.
- **Основание применения «Чеклист осмотра транспорта для подвоза авиагруза к терминалу»** — заявка, приказ, договор, акт, обращение или иной первичный документ, без которого ассистент не должен формировать окончательный вывод.
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
| `vehicle_number` | Номер транспортного средства | `{{vehicle_number}}` |
| `inspection_date` | Дата осмотра | `{{inspection_date}}` |
| `inspector_name` | Наименование инспектора | `{{inspector_name}}` |
| `driver_name` | ФИО водителя | `{{driver_name}}` |
| `brake_status` | Статус тормозов | `{{brake_status}}` |
| `tire_status` | Статус шин | `{{tire_status}}` |
| `light_status` | Статус освещения | `{{light_status}}` |
| `fluid_levels` | Жидкостей уровней | `{{fluid_levels}}` |
| `defect_notes` | Дефекта заметок | `{{defect_notes}}` |

### 3. Подготовка текста

Логист или диспетчер заполняет только подтвержденные поля по booking, AWB/MAWB/HAWB, terminal acceptance,
screening record, CMR/ТТН наземного плеча и фотофиксации. Плейсхолдеры `{{...}}` остаются для несверенных данных
груза, airport pair, пломб, ULD/pallet или ТС наземного плеча; подстановка по аналогии не допускается.

### 4. Текст шаблона

```
Чеклист осмотра транспорта для подвоза авиагруза к терминалу

| Контрольная точка | Данные | ОК | Комментарий |
|-------------------|--------|----|-------------|
| Номер транспортного средства | {{vehicle_number}} | ☐ | |
| Дата осмотра | {{inspection_date}} | ☐ | |
| Наименование инспектора | {{inspector_name}} | ☐ | |
| ФИО водителя | {{driver_name}} | ☐ | |
| Статус тормозов | {{brake_status}} | ☐ | |
| Статус шин | {{tire_status}} | ☐ | |
| Статус освещения | {{light_status}} | ☐ | |
| Жидкостей уровней | {{fluid_levels}} | ☐ | |
| Дефекта заметок | {{defect_notes}} | ☐ | |
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


- Владелец процесса проверяет, что «Чеклист осмотра транспорта для подвоза авиагруза к терминалу»
  применяется к подтвержденной air cargo операции, а не к общей перевозке без booking, AWB/MAWB/HAWB и
  terminal record.
- Рабочий комплект: предрейсовый осмотр ТС, airport pass, пломбы, фото, safety checklist и terminal route.
  CMR/ТТН, GPS и данные водителя используются только для наземного подвоза или вывоза, если этот участок
  связан с airport pair и рейсом.
- Срок реакции: контроль выполняется до выезда на терминальный маршрут; missed cutoff, failed screening,
  offload, customs/security hold, damage/loss или temperature excursion фиксируются в TMS/WMS/terminal log с
  владельцем и следующим сроком.
- Основания для HOLD/STOP: нет осмотра, допуска, пломб, фото или записи о пригодности ТС. Неподтвержденные
  даты, суммы, персональные данные, пломбы, вес, temperature mode и реквизиты не подставляются.
- Маршрут эскалации: fleet owner, dispatcher, QHSE, terminal security и logistics; спорный RAG-ответ, проект
  письма или операционное решение блокируются до закрытия доказательств и решения владельца процесса.
## Stop/go критерии

- GO: ТС допускается на аэропортовый маршрут, если предрейсовый осмотр, safety checklist, фото, пломбы,
  temperature equipment, airport pass и связь с AWB/booking подтверждены.
- HOLD: не закрыты дефекты, нет фото/акта, не подтверждены пломбы, temperature logger, terminal route или
  ответственный за устранение замечаний.
- STOP: неисправность влияет на сохранность груза, controlled-zone safety, temperature mode, dangerous goods
  или выполнение terminal cutoff; выпуск блокируется до QHSE/logistics решения.
## Практический сценарий
- Сценарий: диспетчер или механик применяет «Чеклист осмотра транспорта для подвоза авиагруза к терминалу» перед подвозом/вывозом авиагруза на наземном плече first/last mile.
- Проверить: водителя и ТС наземного аэропортового плеча first/last mile, terminal pass, CMR/ТТН
  наземного плеча, пломбы,
  GPS status, temperature logger, tender/recovery time slot и working time limits.
- Подтвердить источниками: CMR/ТТН наземного плеча, terminal pass, чек-лист ТС, GPS track, temperature
  logger, medical/shift check, repair request и defect фото.
- Результат: выпуск рейса подтверждается чек-листом; критичные отклонения передаются механику и руководителю логистики.
- Предметная проверка: признаки «техосмотр, чеклист, автомобиль, безопасность» сверяются с исходными документами и не используются как общий ярлык.

## Air cargo профиль документа

- Для «Чеклист осмотра транспорта для подвоза авиагруза к терминалу» air cargo профиль строится вокруг
  подтвержденного airport pair, flight number, booking, AWB/MAWB/HAWB, cutoff time, terminal handling,
  security screening, ULD/pallet build-up и chargeable weight.
- Предметная опора документа: предрейсовый осмотр ТС, airport pass, пломбы, фото, safety checklist и
  terminal route. Эти факты должны быть видны в TMS/WMS/terminal log, акте, фото, переписке carrier/GSA или
  связанном документе.
- First/last mile описывает только подвоз или вывоз до аэропорта: CMR/ТТН, водитель, GPS и данные ТС не
  заменяют AWB, terminal acceptance, screening/build-up records и cargo manifest.
- Special cargo требует ручной проверки для dangerous goods, lithium batteries, pharma/cold chain,
  perishables, oversized и valuable cargo; HOLD наступает, если нет осмотра, допуска, пломб, фото или записи
  о пригодности ТС.
- Эскалация идет через fleet owner, dispatcher, QHSE, terminal security и logistics, чтобы документ не
  превращался в общий транспортный шаблон без авиационных доказательств.
## Правила ответа RAG-ассистента

- Использовать документ как источник типа «чеклист» по теме «Чеклист осмотра транспорта для подвоза авиагруза к терминалу» только при фактическом совпадении запроса с предметом документа.
- Перед ответом проверить: airport origin/destination, flight number, booking, AWB/MAWB/HAWB, cutoff time,
  terminal acceptance, security screening, ULD/pallet, gross/chargeable weight, shipper/consignee, carrier/GSA,
  special cargo status;
  для first/last mile проверить ТС, водителя, terminal pass, CMR/ТТН, пломбы, фото, GPS и temperature logger;
  класс опасности/температуру/габариты/chargeable weight/ULD limits и разрешения.
- Если фактов по «Чеклист осмотра транспорта для подвоза авиагруза к терминалу» не хватает, вернуть уточняющие вопросы; даты, суммы, доступы и реквизиты оставлять неподтвержденными до проверки.
- Споры, расчеты, санкции, защищенные категории и персональные данные передавать на ручную проверку.

## Доказательства и источники для ответа

- договор air cargo/экспедиции, booking confirmation, AWB/MAWB/HAWB, cargo manifest и terminal acceptance record.
- данные груза: gross/chargeable weight, dimensions, packaging, marking/labels, temperature mode, dangerous
  goods/lithium status, пломбы, ULD/pallet и фото.
- SDS, shipper's declaration, temperature log, carrier/terminal approval, scale ticket, ULD/pallet build-up
  sheet и securing фото.
- ключевые признаки документа: техосмотр, чеклист, автомобиль, безопасность.
- нормативные ориентиры: Воздушный кодекс РФ; Правила технической эксплуатации.

## Типовые пользовательские запросы

| Запрос пользователя | Безопасная реакция ассистента |
|---------------------|-------------------------------|
| Что проверить по рейсу? | Airport pair, flight, booking, AWB, cutoff, terminal status, cargo, пломбы и фото. |
| Кто отвечает за ущерб или просрочку? | Без AWB, terminal timestamps, актов, фото и carrier evidence не решать. |
| Какие факты нужны для «Чеклист осмотра транспорта для подвоза авиагруза к терминалу»? | Перечислить недостающие даты, документы, участников, суммы/сроки и ответственных. |
| Можно ли применять автоматически? | Только после проверки ограничений по «Чеклист осмотра транспорта для подвоза авиагруза к терминалу»; при риске или неполных фактах нужна ручная проверка. |

## Ответственные роли

| Роль | Зона ответственности |
|------|----------------------|
| Директор по логистике | утверждает применение правила и дату актуальности источника |
| Логист/диспетчер | проверяет airport pair, flight, booking, AWB, cargo, terminal, carrier/GSA и наземное плечо |
| Терминал / склад / наземное плечо | передает для «Чеклист осмотра транспорта для подвоза авиагруза к терминалу» booking, AWB, terminal records, CMR/ТТН и GPS только как first/last mile evidence |
| Юрист/Compliance | оценивает вывод об ответственности без AWB, terminal актов, фото и carrier evidence |

## Риски и ограничения

- Нельзя отвечать без проверки: водителя и ТС наземного аэропортового плеча first/last mile, terminal pass, CMR/ТТН
  наземного плеча, пломбы, GPS status, temperature logger, tender/recovery time slot и working time limits.
- ключевые признаки (техосмотр, чеклист, автомобиль, безопасность) могут быть неверно применены без документа-основания.
- вывод об ответственности без AWB/MAWB/HAWB, terminal act, фото, flight status, объяснения
  перевозчика/терминала и доказательства наземного плеча.
- расхождение airport pair, flight number, cargo, gross/chargeable weight, пломбы, ULD/pallet или temperature
  mode между booking, AWB/MAWB/HAWB и terminal records.
- air cargo booking выпущен без carrier approval, DGR/cold-chain/oversized разрешений, temperature control,
  screening или chargeable weight check.
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
- Правила технической эксплуатации

## Критерии качества ответа

- ответ решает именно сценарий «Чеклист осмотра транспорта для подвоза авиагруза к терминалу» и не подменяет его общим правилом категории.
- проверено: водителя и ТС наземного аэропортового плеча first/last mile, terminal pass, CMR/ТТН
  наземного плеча, пломбы,
  GPS status, temperature logger, tender/recovery time slot и working time limits.
- источники подтверждения: CMR/ТТН наземного плеча, terminal pass, чек-лист ТС, GPS track, temperature
  logger, medical/shift check, repair request и defect фото.
- учтен профильный риск: выезд на наземное плечо first/last mile выполнен без terminal pass,
  проверки ТС/водителя, seal, GPS,
  temperature logger или defect closure.
- ключевые признаки (техосмотр, чеклист, автомобиль, безопасность) использованы только вместе с подтвержденными документами.
- не подставлены airport pair, flight, chargeable weight, пломбы, температура, водитель/ТС наземного плеча,
  CMR/ТТН наземного плеча или акты без air cargo документов.
## Контрольный список

- [ ] запрос сопоставлен с документом «Чеклист осмотра транспорта для подвоза авиагруза к терминалу» и типом «чеклист»
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
- [ ] недостающие факты по «Чеклист осмотра транспорта для подвоза авиагруза к терминалу» вынесены в уточняющие вопросы

## Порядок пересмотра и актуализации

Владелец документа: Директор по логистике. Плановый пересмотр проводится не реже одного раза в 12 месяцев, а
также при изменении законодательства, организационной структуры, маршрута согласования, ответственных ролей или
используемых шаблонов. Изменения вступают в силу после утверждения владельцем процесса и доведения до
сотрудников или контрагентов, которых затрагивает документ.

## История изменений

| Версия | Дата | Изменение | Автор |
|--------|------|-----------|-------|
| 1.0 | 2026-05-15 | Первичная редакция внутреннего документа | Владелец процесса |

> Применять «Чеклист осмотра транспорта для подвоза авиагруза к терминалу» после подтверждения владельцем процесса; спорные и нетиповые кейсы требуют ручной проверки.
