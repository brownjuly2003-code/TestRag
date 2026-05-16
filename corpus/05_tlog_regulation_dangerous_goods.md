---
doc_id: tlog_regulation_dangerous_goods
title: Инструкция по air cargo dangerous goods
category: Transport and logistics legal docs
document_type: инструкция
department: Logistics
synthetic_demo: false
source_type: internal_controlled
version: "1.0"
effective_date: '2026-05-15'
owner_role: Директор по логистике
related_normative_sources:
- IATA Dangerous Goods Regulations (DGR)
- IATA lithium battery и dry ice requirements
- Воздушный кодекс РФ
keywords:
- опасные грузы
- IATA DGR
- UN номер
- инструкция
confidentiality: internal
---

# Инструкция по air cargo dangerous goods

## Назначение

Установить правила air cargo dangerous goods по IATA DGR, airline approval, shipper's declaration, lithium battery restrictions и российским авиационным требованиям. Сотрудник логистического контура сверяет air cargo booking, AWB/MAWB/HAWB, аэропорт отправления и назначения, номер рейса, cutoff time, terminal handling, security screening, ULD/pallet build-up, chargeable weight, пломбы, фотофиксацию и GPS/температурные данные наземного плеча; решение о допуске груза к авиарейсу принимается только после устранения расхождений и подтверждения терминала или авиаперевозчика.

## Область применения

Документ «Инструкция по air cargo dangerous goods» применяется при air cargo booking, tender to terminal, terminal acceptance, security screening, ULD/pallet build-up, handover to airline, arrival и recovery. Расхождения по airport pair, flight number, AWB/MAWB/HAWB, chargeable weight, пломбам, температуре, security или customs status фиксируются актом в TMS/WMS/terminal log до закрытия операции и передаются логисту и юристу до претензии или ответа контрагенту.

## Термины

- **Рабочий экземпляр «Инструкция по air cargo dangerous goods»** — версия документа с датой, владельцем процесса, статусом согласования и приложениями, по которой можно принимать внутреннее решение.
- **Основание применения «Инструкция по air cargo dangerous goods»** — заявка, приказ, договор, акт, обращение или иной первичный документ, без которого ассистент не должен формировать окончательный вывод.
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
| `cargo_un_number` | Номер груза UN | `{{cargo_un_number}}` |
| `cargo_class` | Класс груза | `{{cargo_class}}` |
| `driver_adr_certificate` | DGR/ADR допуск водителя наземного плеча | `{{driver_adr_certificate}}` |
| `vehicle_adr_certificate` | DGR/ADR допуск ТС наземного плеча | `{{vehicle_adr_certificate}}` |
| `route_approval` | Маршрут согласования | `{{route_approval}}` |
| `emergency_card_number` | Номер аварийной карточки | `{{emergency_card_number}}` |
| `escort_vehicle_flag` | Признак машины сопровождения | `{{escort_vehicle_flag}}` |

### 3. Подготовка текста

Ответственный сотрудник сверяет каждое поле с первичными источниками рейса: air cargo booking, AWB/MAWB/HAWB,
договором перевозки/экспедиции, terminal acceptance, screening record, ULD/pallet build-up sheet, пломбами,
GPS-треком наземного плеча и температурным листом. Незаполненные значения остаются плейсхолдерами `{{...}}` до
устранения расхождений.

### 4. Текст шаблона

```
Инструкция по air cargo dangerous goods

1. Исходные параметры air cargo операции
- Booking: {{booking_number}}
- AWB/MAWB/HAWB: {{awb_number}} / {{mawb_number}} / {{hawb_number}}
- Аэропорт отправления / назначения: {{airport_origin}} / {{airport_destination}}
- Номер авиарейса и cutoff time: {{flight_number}} / {{cutoff_time}}
- ULD/pallet и chargeable weight: {{uld_or_pallet_id}} / {{chargeable_weight}}
- Terminal handling / security screening: {{terminal_handling_status}} / {{security_screening_status}}
- Номер груза UN: {{cargo_un_number}}
- Класс груза: {{cargo_class}}
- DGR/ADR допуск водителя наземного плеча: {{driver_adr_certificate}}
- DGR/ADR допуск ТС наземного плеча: {{vehicle_adr_certificate}}
- Маршрут согласования: {{route_approval}}
- Номер аварийной карточки: {{emergency_card_number}}
- Признак машины сопровождения: {{escort_vehicle_flag}}

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

Операционный документ «Инструкция по air cargo dangerous goods» согласуют air cargo operations, диспетчер смены, WMS/склад, terminal representative и carrier/GSA; юрист подключается при damage/loss, offload, missed cutoff, customs/security hold, temperature excursion, terminal charges, insurance regress или инцидент на наземном плече first/last mile. Расхождения по airport pair, flight, AWB/MAWB/HAWB, грузу, пломбам, gross/chargeable weight, температуре, ULD/pallet или комплектности фиксируются актом и фотофиксацией до закрытия air cargo operation.

### 6. Регистрация и хранение

Финальная версия и подтверждающие материалы хранятся в карточке air cargo operation в TMS/WMS/terminal log:
booking, AWB/MAWB/HAWB, cargo manifest, terminal acceptance, screening record, ULD/pallet build-up sheet, акты,
фото, temperature logger, GPS-трек наземного плеча и переписка; доступ получают logistics, terminal/warehouse,
finance, insurance и юристы при споре.


## Рабочие доказательства, сроки и эскалация


- Владелец процесса проверяет, что «Инструкция по air cargo dangerous goods» применяется к подтвержденной
  air cargo операции, а не к общей перевозке без booking, AWB/MAWB/HAWB и terminal record.
- Рабочий комплект: DGR declaration, UN number, packing instruction, labels, lithium status и acceptance
  check. CMR/ТТН, GPS и данные водителя используются только для наземного подвоза или вывоза, если этот
  участок связан с airport pair и рейсом.
- Срок реакции: контроль выполняется до booking confirmation и terminal tender; missed cutoff, failed
  screening, offload, customs/security hold, damage/loss или temperature excursion фиксируются в
  TMS/WMS/terminal log с владельцем и следующим сроком.
- Основания для HOLD/STOP: нет DGR декларации, маркировки, packing instruction или trained person approval.
  Неподтвержденные даты, суммы, персональные данные, пломбы, вес, temperature mode и реквизиты не
  подставляются.
- Маршрут эскалации: DG specialist, terminal acceptance, carrier/GSA, QHSE и compliance; спорный RAG-ответ,
  проект письма или операционное решение блокируются до закрытия доказательств и решения владельца процесса.
## Практический сценарий
- Сценарий: диспетчер проверяет специальный груз по «Инструкция по air cargo dangerous goods» перед подтверждением booking, terminal slot и наземного плеча first/last mile.
- Проверить: UN number/class, packing instruction, lithium battery status, gross/chargeable weight, dimensions,
  temperature profile, IATA DGR permissions, airline approval, ULD/pallet compatibility и terminal capability.
- Подтвердить источниками: SDS, shipper's declaration, IATA DGR/lithium declaration, temperature record, carrier
  approval, scale ticket, ULD/pallet build-up sheet и securing фото.
- Результат: booking/tender блокируется до carrier approval, terminal capability confirmation, screening plan,
  ULD/pallet approval и monitoring milestones.
- Предметная проверка: признаки «dangerous goods, IATA DGR, lithium batteries, UN number, air cargo instruction» сверяются с исходными документами и не используются как общий ярлык.

## Air cargo профиль документа

- Для «Инструкция по air cargo dangerous goods» air cargo профиль строится вокруг подтвержденного airport
  pair, flight number, booking, AWB/MAWB/HAWB, cutoff time, terminal handling, security screening,
  ULD/pallet build-up и chargeable weight.
- Предметная опора документа: DGR declaration, UN number, packing instruction, labels, lithium status и
  acceptance check. Эти факты должны быть видны в TMS/WMS/terminal log, акте, фото, переписке carrier/GSA
  или связанном документе.
- First/last mile описывает только подвоз или вывоз до аэропорта: CMR/ТТН, водитель, GPS и данные ТС не
  заменяют AWB, terminal acceptance, screening/build-up records и cargo manifest.
- Special cargo требует ручной проверки для dangerous goods, lithium batteries, pharma/cold chain,
  perishables, oversized и valuable cargo; HOLD наступает, если нет DGR декларации, маркировки, packing
  instruction или trained person approval.
- Эскалация идет через DG specialist, terminal acceptance, carrier/GSA, QHSE и compliance, чтобы документ не
  превращался в общий транспортный шаблон без авиационных доказательств.
## Правила ответа RAG-ассистента

- Использовать документ как источник типа «инструкция» по теме «Инструкция по air cargo dangerous goods» только при фактическом совпадении запроса с предметом документа.
- Перед ответом проверить: airport origin/destination, flight number, booking, AWB/MAWB/HAWB, cutoff time,
  terminal acceptance, security screening, ULD/pallet, gross/chargeable weight, shipper/consignee, carrier/GSA,
  special cargo status; для first/last mile проверить ТС, водителя, terminal pass, CMR/ТТН,
  пломбы, фото, GPS и temperature logger.
- Если фактов по «Инструкция по air cargo dangerous goods» не хватает, вернуть уточняющие вопросы; даты, суммы, доступы и реквизиты оставлять неподтвержденными до проверки.
- Споры, расчеты, санкции, защищенные категории и персональные данные передавать на ручную проверку.

## Доказательства и источники для ответа

- договор air cargo/экспедиции, booking confirmation, AWB/MAWB/HAWB, cargo manifest и terminal acceptance record.
- данные груза: gross/chargeable weight, dimensions, packaging, marking/labels, temperature mode, dangerous
  goods/lithium status, пломбы, ULD/pallet и фото.
- booking, AWB/MAWB/HAWB, terminal log, screening record, акт, фото, GPS наземного плеча и temperature logger.
- SDS, shipper's declaration, temperature log, carrier/terminal approval, scale ticket, ULD/pallet build-up
  sheet и securing фото.
- спецификация, счет, УПД, сертификаты качества, акт расхождений и рекламация.
- ключевые признаки документа: dangerous goods, IATA DGR, lithium batteries, UN number, air cargo instruction.
- нормативные ориентиры: IATA Dangerous Goods Regulations (DGR); IATA Dangerous Goods Regulations; Воздушный кодекс РФ.

## Типовые пользовательские запросы

| Запрос пользователя | Безопасная реакция ассистента |
|---------------------|-------------------------------|
| Что проверить по рейсу? | Airport pair, flight, booking, AWB, cutoff, terminal status, cargo, пломбы и фото. |
| Кто отвечает за ущерб или просрочку? | Без AWB, terminal timestamps, актов, фото и carrier evidence не решать. |
| Какие факты нужны для «Инструкция по air cargo dangerous goods»? | Перечислить недостающие даты, документы, участников, суммы/сроки и ответственных. |
| Можно ли применять автоматически? | Только после проверки ограничений по «Инструкция по air cargo dangerous goods»; при риске или неполных фактах нужна ручная проверка. |

## Ответственные роли

| Роль | Зона ответственности |
|------|----------------------|
| Директор по логистике | утверждает применение правила и дату актуальности источника |
| Логист/диспетчер | проверяет airport pair, flight, booking, AWB, cargo, terminal, carrier/GSA и наземное плечо |
| Терминал / склад / наземное плечо | передает для «Инструкция по air cargo dangerous goods» booking, AWB, terminal records, CMR/ТТН и GPS только как first/last mile evidence |
| Юрист/Compliance | оценивает вывод об ответственности без AWB, terminal актов, фото и carrier evidence |

## Риски и ограничения

- Нельзя отвечать без проверки: UN number/class, packing instruction, lithium battery status, gross/chargeable
  weight, dimensions, temperature profile, IATA DGR permissions, airline approval, ULD/pallet compatibility и
  terminal capability.
- ключевые признаки (dangerous goods, IATA DGR, lithium batteries, UN number, air cargo instruction) могут быть неверно применены без документа-основания.
- вывод об ответственности без AWB/MAWB/HAWB, terminal act, фото, flight status, объяснения
  перевозчика/терминала и доказательства наземного плеча.
- расхождение airport pair, flight number, cargo, gross/chargeable weight, пломбы, ULD/pallet или temperature
  mode между booking, AWB/MAWB/HAWB и terminal records.
- несовпадение cargo, airport pair, flight, пломбы, cutoff, terminal SLA или chargeable weight в договоре,
  booking и AWB/MAWB/HAWB.
- air cargo booking выпущен без carrier approval, DGR/cold-chain/oversized разрешений, temperature control,
  screening или chargeable weight check.
- terminal acceptance без проверки packages, cargo condition, documents, AWB, screening и special cargo restrictions.
## Связанные документы

- `MANIFEST.md`
- `NORMATIVE_SOURCE_MANIFEST.md`
- `05_tlog_contract_transport_air.md`
- `05_tlog_regulation_dispatch.md`
- `05_tlog_checklist_cargo_acceptance.md`
- `04_legal_claim_cargo_damage.md`

## Нормативные ориентиры

- IATA Dangerous Goods Regulations (DGR)
- IATA lithium battery и dry ice requirements
- Воздушный кодекс РФ

## Критерии качества ответа

- ответ решает именно сценарий «Инструкция по air cargo dangerous goods» и не подменяет его общим правилом категории.
- проверено: UN number/class, packing instruction, lithium battery status, gross/chargeable weight, dimensions,
  temperature profile, IATA DGR permissions, airline approval, ULD/pallet compatibility и terminal capability.
- источники подтверждения: SDS, shipper's declaration, IATA DGR/lithium declaration, temperature record, carrier
  approval, scale ticket, ULD/pallet build-up sheet и securing фото.
- учтен профильный риск: air cargo booking/tender выпущен без carrier approval, screening,
  DGR/cold-chain/oversized разрешений, temperature control или chargeable weight confirmation.
- ключевые признаки (dangerous goods, IATA DGR, lithium batteries, UN number, air cargo instruction) использованы только вместе с подтвержденными документами.
- не подставлены airport pair, flight, chargeable weight, пломбы, температура, водитель/ТС наземного плеча,
  CMR/ТТН наземного плеча или акты без air cargo документов.
## Контрольный список

- [ ] запрос сопоставлен с документом «Инструкция по air cargo dangerous goods» и типом «инструкция»
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
- [ ] недостающие факты по «Инструкция по air cargo dangerous goods» вынесены в уточняющие вопросы

## Порядок пересмотра и актуализации

Владелец документа: Директор по логистике. Плановый пересмотр проводится не реже одного раза в 12 месяцев, а
также при изменении законодательства, организационной структуры, маршрута согласования, ответственных ролей или
используемых шаблонов. Изменения вступают в силу после утверждения владельцем процесса и доведения до
сотрудников или контрагентов, которых затрагивает документ.

## История изменений

| Версия | Дата | Изменение | Автор |
|--------|------|-----------|-------|
| 1.0 | 2026-05-15 | Первичная редакция внутреннего документа | Владелец процесса |

> Применять «Инструкция по air cargo dangerous goods» после подтверждения владельцем процесса; спорные и нетиповые кейсы требуют ручной проверки.
