---
doc_id: legal_contract_expedition_international
title: Договор международной экспедиции
category: Legal contract templates
document_type: договор транспортной экспедиции
department: Legal
synthetic_demo: false
source_type: internal_controlled
version: "1.0"
effective_date: '2026-05-15'
owner_role: Руководитель юридического отдела
related_normative_sources:
- ГК РФ, глава 41 (транспортная экспедиция)
- ТК ВЭД (Таможенный кодекс ЕАЭС)
- ФЗ от 08.11.2007 № 259-ФЗ
keywords:
- международная экспедиция
- таможня
- CMR наземного плеча
- TIR
confidentiality: internal
---

# Договор международной экспедиции

## Назначение

Договор международной экспедиции используется для сценария: экспедитор ведет экспорт/импорт, customs, transit
evidence и наземное плечо, связанное с AWB. Это рабочий шаблон Legal для авиагрузовой сделки, где предмет
проверяется по источникам, а не по названию документа.

До выпуска проекта юрист сверяет полномочия, приложения, лимиты ответственности, страхование и доказательства:
export booking, MAWB/HAWB, invoice, packing list, customs declaration, permits, CMR/TIR наземного плеча, carrier
notices. AWB/MAWB/HAWB, airport, flight, terminal, customs и dangerous goods указываются только как условия или
ограничения.

## Область применения

Документ применяется, когда запрос связан с профилем «международная air cargo экспедиция» и есть операционная
связка с air cargo route, terminal handover или расчетами по перевозке.

Наземное или транзитное плечо допускается только как evidence международной экспедиции: CMR/TIR, customs transit
и связь с MAWB/HAWB. Customs/export control, dangerous goods, temperature-controlled cargo и security screening включаются
только при подтвержденной применимости.

## Термины

- **Международная air cargo экспедиция** — профиль документа, который определяет обязательные приложения и
  evidence.
- **Aviation evidence по сделке** — export booking, MAWB/HAWB, invoice, packing list, customs declaration,
  permits, CMR/TIR наземного плеча, carrier notices; комплект подтверждает предмет, цену, сроки, приемку и
  пределы ответственности.
- **Операционное ограничение** — маршрут запускается без export control, санкционной проверки, разрешений или
  стыковки customs deadline с flight cutoff; условие выносится в приложение, SLA или протокол разногласий.
- **Эскалационное событие** — customs hold, denied party match, rebooking, transit storage или спор по
  документам отправителя; после него проект возвращается к Legal, operations и finance/insurance.

## Порядок действий

### 1. Инициирование

Инициатор сделки передает в юридический отдел заявку с авиационным предметом, контрагентом, коммерческими
условиями, AWB/booking или описанием планируемой отправки, аэропортами, рейсом, cutoff time, cargo terminal/GHA,
special cargo режимом, SLA, страхованием, лимитами ответственности и желаемой датой подписания. Юрист начинает
работу после проверки полномочий подписантов, карточки контрагента, маршрута согласования и версии приложений.

### 2. Обязательные поля

| Поле | Назначение | Пример заполнения |
|------|------------|-------------------|
| `contract_number` | Номер договора | `{{contract_number}}` |
| `contract_date` | Дата договора | `{{contract_date}}` |
| `forwarder_name` | Наименование экспедитора | `{{forwarder_name}}` |
| `client_name` | Наименование клиента | `{{client_name}}` |
| `origin_country` | Отправления страны | `{{origin_country}}` |
| `destination_country` | Назначения страны | `{{destination_country}}` |
| `customs_broker_terms` | Условия таможенного брокера | `{{customs_broker_terms}}` |
| `freight_cost` | Стоимость фрахта | `{{freight_cost}}` |
| `currency` | Валюты | `{{currency}}` |
| `incoterms` | Incoterms | `{{incoterms}}` |
| `mawb_hawb` | MAWB/HAWB | `{{mawb_hawb}}` |
| `booking_ref` | Booking reference | `{{booking_ref}}` |
| `flight_number` | Flight number | `{{flight_number}}` |
| `airport_pair` | Airport of departure/destination | `{{airport_pair}}` |
| `chargeable_weight` | Chargeable weight | `{{chargeable_weight}}` |
| `special_cargo_status` | Dangerous goods/temperature status | `{{special_cargo_status}}` |

### 3. Подготовка текста

Ответственный юрист сверяет каждое поле с первичными источниками: заявку инициатора, карточку контрагента,
полномочия подписанта, коммерческое предложение, тарифы, SLA и приложения к авиагрузовой операции. Незаполненные
значения остаются плейсхолдерами `{{...}}`; AWB, booking, рейс, аэропорты, цена, штрафы, лимиты ответственности
и сроки приемки не подставляются по образцу другого договора.

### 4. Текст шаблона

```
ДОГОВОР МЕЖДУНАРОДНОЙ ЭКСПЕДИЦИИ

г. {{city}}                                      {{contract_date}}

1. Стороны и полномочия
1.1. Сторона 1: {{party_1_name}}, представитель: {{party_1_representative}}.
1.2. Сторона 2: {{party_2_name}}, представитель: {{party_2_representative}}.
1.3. Полномочия подписантов подтверждаются уставом, доверенностью, решением органа управления или доверенностью
     на работу с авиагрузовыми документами.

2. Предмет и авиационные параметры
2.1. Предмет: международная air cargo экспедиция с export/import customs, MAWB/HAWB, transit documents,
     permits и стыковкой terminal handling с flight cutoff.
2.2. Существенные параметры сделки:
- Номер договора: {{contract_number}}
- Дата договора: {{contract_date}}
- Наименование экспедитора: {{forwarder_name}}
- Наименование клиента: {{client_name}}
- Отправления страны: {{origin_country}}
- Назначения страны: {{destination_country}}
- Условия таможенного брокера: {{customs_broker_terms}}
- Стоимость фрахта: {{freight_cost}}
- Валюты: {{currency}}
- Incoterms: {{incoterms}}
- MAWB/HAWB: {{mawb_hawb}}
- Booking reference: {{booking_ref}}
- Flight number: {{flight_number}}
- Airport of departure/destination: {{airport_pair}}
- Chargeable weight: {{chargeable_weight}}
- Dangerous goods/temperature status: {{special_cargo_status}}
2.3. В заявке или приложении указываются AWB/MAWB/HAWB или booking, flight number, airport of
     departure/destination, cutoff time, chargeable weight, terminal handling, ULD/pallet, customs/export
     control и special cargo requirements, если они применимы к операции.
2.4. Наземное или транзитное плечо допускается только как evidence международной экспедиции: CMR/TIR,
     customs transit и связь с MAWB/HAWB.

3. Цена, сроки, SLA и приемка
3.1. Цена, валюта, freight/handling/storage charges, порядок оплаты и chargeable weight указываются по
     согласованным тарифам, rate sheet или коммерческому предложению.
3.2. Исполнение подтверждается: export booking, MAWB/HAWB, invoice, packing list, customs declaration,
     permits, CMR/TIR наземного плеча и carrier notices.
3.3. Повреждение, недостача, задержка рейса, отказ авиаперевозчика в приемке, missed cutoff или нарушение
     температуры фиксируются актом cargo terminal/GHA, фото, журналом событий, temperature log и уведомлением
     другой стороны.
3.4. Для dangerous goods, lithium batteries, pharma/cold chain, valuable cargo и export control требуются
     отдельные документы, разрешения и подтверждение перевозчика или терминала.

4. Ответственность, страхование и ограничения
4.1. Неустойка, лимит ответственности, страхование и возмещение убытков применяются только при прямом указании в
     договоре, SLA, AWB/booking или страховом покрытии.
4.2. Стороны отдельно распределяют ответственность за terminal handling, customs delay, отказ в приемке,
     temperature excursion, cargo data и действия carrier, GHA, broker и first/last mile подрядчиков.
4.3. Санкционные, таможенные, export control, dangerous goods и персональные данные требуют ручной проверки
     юриста и compliance.

Сторона 1 __________________ / {{party_1_representative}} /
Сторона 2 __________________ / {{party_2_representative}} /
```

### 5. Согласование

Проект согласуют юрист, финансы, air cargo operations и compliance; GHA/терминал, customs broker, страховая или
технический владелец подключаются, если предмет затрагивает handling, customs/export control, insurance, special
cargo, cargo data или оборудование авиационного контура. Любая правка AWB/booking, тарифа, SLA, liability cap
или special cargo условий возвращает проект на повторное согласование.

### 6. Подписание и хранение

Подписанная версия, приложения, AWB/booking evidence, протоколы разногласий, подтверждение полномочий и
страховые/таможенные документы хранятся в системе договорного учета. Рабочие проекты не заменяют подписанный
экземпляр и не используются для расчетов, приемки груза или претензий без финальной версии.

## Рабочие доказательства, сроки и эскалация

- Владелец процесса проверяет профиль «международная air cargo экспедиция», стороны, authority matrix,
  коммерческие условия и evidence: export booking, MAWB/HAWB, invoice, packing list, customs declaration,
  permits, CMR/TIR наземного плеча, carrier notices.
- Срок первичной юридической проверки — 2 рабочих дня после получения полного комплекта; для dangerous goods,
  санкций, insurance gap или airport security срок фиксируется отдельно.
- Эскалация обязательна при событии: customs hold, denied party match, rebooking, transit storage или спор по
  документам отправителя. Решение фиксируется в версии договора, приложении, протоколе разногласий или change
  log.
- Нельзя переносить AWB, flight number, airport pair, terminal status, customs status, chargeable weight или
  сумму из похожей сделки без первичного источника.

## Практический сценарий

- Сценарий: экспедитор организует международный air freight с HAWB, экспортным оформлением и terminal handling.
- Проверить: export/import маршрут, MAWB/HAWB, permits, customs declaration, denied-party screening,
  transit storage, flight number, airport pair и special cargo status.
- Подтвердить источниками: export booking, MAWB/HAWB, invoice, packing list, customs declaration, permits,
  CMR/TIR наземного плеча и carrier notices.
- Результат: проект содержит aviation-specific предмет, route/airport details, приемочные доказательства,
  liability cap, страхование, порядок претензий и ручную проверку special cargo/customs рисков.
- Предметная проверка: признаки «международная экспедиция, таможня, CMR/TIR наземного плеча» используются только вместе с подтвержденными AWB/booking, приложениями и операционными документами.

## Правила ответа RAG-ассистента

- Использовать документ как источник типа «договор транспортной экспедиции» по теме «Договор международной экспедиции» только при совпадении запроса с авиагрузовым предметом документа.
- Перед ответом проверить: export/import route, permits, customs deadline, MAWB/HAWB, booking, airport pair,
  chargeable weight, special cargo, полномочия подписантов и версию приложений.
- Если нет AWB/booking, flight number, airport pair, cargo terminal status, цены, срока, акта приемки или
  ключевого факта, сначала вернуть уточняющие вопросы и не подставлять данные по догадке.
- Dangerous goods, temperature, customs/export control, санкции, валюту, страхование и cargo data передавать на
  ручную проверку.

## Доказательства и источники для ответа

- Профильные источники: export booking, MAWB/HAWB, invoice, packing list, customs declaration, permits, CMR/TIR
  наземного плеча, carrier notices.
- Корпоративные источники: заявка инициатора, карточка контрагента, authority matrix, коммерческое предложение,
  приложения, страховой или финансовый approval.
- Ограничение для ответа: маршрут запускается без export control, санкционной проверки, разрешений или стыковки
  customs deadline с flight cutoff. Если источник не подтверждает его, RAG-ответ указывает пробел и не подменяет
  его общей договорной нормой.
- Airport, flight, terminal, customs и dangerous goods используются как проверяемые факты: дата, статус, акт,
  разрешение, отметка или запрет.

## Типовые пользовательские запросы

| Запрос пользователя | Безопасная реакция ассистента |
|---------------------|-------------------------------|
| Подходит ли «Договор международной экспедиции» для авиагрузовой сделки? | Сопоставить предмет, стороны, AWB/booking, аэропорты, SLA, special cargo и обязательные приложения; назвать недостающие факты и риски. |
| Сделай черновик договора. | Собрать поля; не выдумывать цену, рейс, AWB, cutoff time и реквизиты. |
| Документы для air cargo? | AWB, booking, invoice, packing list, акты, SLA, страхование, customs/export control. |
| Можно ли применить автоматически? | Проверить DG, temperature, customs/export control, sanctions и liability cap. |

## Ответственные роли

| Роль | Зона ответственности |
|------|----------------------|
| Руководитель юридического отдела | утверждает позицию по профилю «международная air cargo экспедиция», liability cap, waiver и нестандартные приложения |
| International forwarding lead | подтверждает operational facts: export booking, MAWB/HAWB, invoice, packing list, customs declaration, permits, CMR/TIR наземного плеча, carrier notices |
| Finance / insurance owner | сверяет тарифы, оплату, reserves, страховое покрытие, deductible и право регресса |
| Compliance / customs contact | проверяет для «Договор международной экспедиции» sanctions/export control, dangerous goods, airport security и ограничения передачи данных |

## Риски и ограничения

- Нельзя готовить договор или RAG-ответ без evidence по профилю «международная air cargo экспедиция»: export
  booking, MAWB/HAWB, invoice, packing list, customs declaration, permits, CMR/TIR наземного плеча, carrier
  notices.
- Ключевой риск сценария: маршрут запускается без export control, санкционной проверки, разрешений или стыковки
  customs deadline с flight cutoff.
- AWB/MAWB/HAWB, flight, airport, terminal и customs status не доказывают ответственность сами по себе; нужна
  связь с обязанностью стороны, сроком, приемкой, ущербом или оплатой.
- Фидерные, first/last mile и иные мультимодальные формулировки допустимы только как
  конкретный handover/proof of delivery, связанный с AWB/booking.

## Связанные документы

- `MANIFEST.md`
- `NORMATIVE_SOURCE_MANIFEST.md`
- `03_legal_contract_services_general.md`
- `03_legal_contract_supply_goods.md`
- `04_legal_claim_non_payment.md`
- `04_legal_memo_contract_breach.md`

## Нормативные ориентиры

- ГК РФ, глава 41 (транспортная экспедиция)
- ТК ВЭД (Таможенный кодекс ЕАЭС)
- ФЗ от 08.11.2007 № 259-ФЗ

## Критерии качества ответа

- ответ решает именно сценарий «международная air cargo экспедиция» и не смешивает его со смежным договором или
  претензией
- источники подтверждения названы предметно: export booking, MAWB/HAWB, invoice, packing list, customs
  declaration, permits, CMR/TIR наземного плеча, carrier notices
- учтен профильный риск: маршрут запускается без export control, санкционной проверки, разрешений или стыковки
  customs deadline с flight cutoff
- если airport, flight, terminal, customs или dangerous goods не подтверждены документом, ответ запрашивает
  источник и не делает вывод по аналогии

## Контрольный список

- [ ] запрос сопоставлен с документом «Договор международной экспедиции» и профилем «международная air cargo
  экспедиция»
- [ ] собраны профильные evidence: export booking, MAWB/HAWB, invoice, packing list, customs declaration,
  permits, CMR/TIR наземного плеча, carrier notices
- [ ] проверены полномочия подписанта, версия приложений, liability cap, insurance и payment terms
- [ ] оценено ограничение: маршрут запускается без export control, санкционной проверки, разрешений или стыковки
  customs deadline с flight cutoff
- [ ] customs/export control, dangerous goods, temperature или security условия включены только при
  подтвержденной применимости

## Порядок пересмотра и актуализации

Владелец документа: Руководитель юридического отдела. Плановый пересмотр проводится не реже одного раза в 12
месяцев.

Внеплановый пересмотр нужен после события: customs hold, denied party match, rebooking, transit storage или спор
по документам отправителя; также после изменения carrier/GHA rules, airport security требований, customs/export
control режима, страхового покрытия или судебной практики.

При пересмотре Legal выборочно сверяет 3-5 завершенных кейсов профиля «международная air cargo экспедиция» и
обновляет evidence list, сроки согласования, роли эскалации и ограничения RAG-ответа.

## История изменений

| Версия | Дата | Изменение | Автор |
|--------|------|-----------|-------|
| 1.0 | 2026-05-15 | Первичная редакция внутреннего документа | Владелец процесса |

> Применять «Договор международной экспедиции» после подтверждения владельцем процесса; спорные и нетиповые кейсы требуют ручной проверки.
