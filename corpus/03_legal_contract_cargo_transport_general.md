---
doc_id: legal_contract_cargo_transport_general
title: Договор перевозки груза (общий шаблон)
category: Legal contract templates
document_type: договор перевозки груза
department: Legal
synthetic_demo: false
source_type: internal_controlled
version: "1.0"
effective_date: '2026-05-15'
owner_role: Руководитель юридического отдела
related_normative_sources:
- ГК РФ, глава 40 (перевозка)
- ФЗ от 08.11.2007 № 259-ФЗ
keywords:
- перевозка
- груз
- договор
- перевозчик
confidentiality: internal
---

# Договор перевозки груза (общий шаблон)

## Назначение

Договор перевозки груза (общий шаблон) используется для сценария: перевозчик принимает груз по AWB/MAWB/HAWB и
доставляет его между аэропортами. Это рабочий шаблон Legal для авиагрузовой сделки, где предмет проверяется по
источникам, а не по названию документа.

До выпуска проекта юрист сверяет полномочия, приложения, лимиты ответственности, страхование и доказательства:
booking, AWB/MAWB/HAWB, cargo manifest, flight status, terminal acceptance, weight note, special cargo approval.
AWB/MAWB/HAWB, airport, flight, terminal, customs и dangerous goods указываются только как условия или
ограничения.

## Область применения

Документ применяется, когда запрос связан с профилем «авиаперевозка груза» и есть операционная связка с air
cargo route, terminal handover или расчетами по перевозке.

Мультимодальное плечо допускается только как evidence к авиаперевозке: отдельный срок передачи в cargo terminal,
акт handover и связь с AWB/booking. Customs/export control, dangerous goods, temperature-controlled cargo и security
screening включаются только при подтвержденной применимости.

## Термины

- **Авиаперевозка груза** — профиль документа, который определяет обязательные приложения и evidence.
- **Aviation evidence по сделке** — booking, AWB/MAWB/HAWB, cargo manifest, flight status, terminal acceptance,
  weight note, special cargo approval; комплект подтверждает предмет, цену, сроки, приемку и пределы
  ответственности.
- **Операционное ограничение** — перевозка описана без аэропортов, cutoff, chargeable weight, acceptance/release
  и special cargo; условие выносится в приложение, SLA или протокол разногласий.
- **Эскалационное событие** — offload, missed cutoff, damage report, customs hold или отказ в приемке dangerous
  goods; после него проект возвращается к Legal, operations и finance/insurance.

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
| `carrier_name` | Наименование перевозчика | `{{carrier_name}}` |
| `shipper_name` | Наименование грузоотправителя | `{{shipper_name}}` |
| `cargo_description` | Описание груза | `{{cargo_description}}` |
| `route` | Маршрут | `{{route}}` |
| `transport_mode` | Вид транспорта | `{{transport_mode}}` |
| `freight_cost` | Стоимость фрахта | `{{freight_cost}}` |
| `delivery_deadline` | Срок доставки | `{{delivery_deadline}}` |
| `awb_number` | AWB/MAWB/HAWB | `{{awb_number}}` |
| `booking_ref` | Booking reference | `{{booking_ref}}` |
| `flight_number` | Flight number | `{{flight_number}}` |
| `airport_departure` | Аэропорт отправления | `{{airport_departure}}` |
| `airport_destination` | Аэропорт назначения | `{{airport_destination}}` |
| `cutoff_time` | Cutoff time | `{{cutoff_time}}` |
| `chargeable_weight` | Chargeable weight | `{{chargeable_weight}}` |

### 3. Подготовка текста

Ответственный юрист сверяет каждое поле с первичными источниками: заявку инициатора, карточку контрагента,
полномочия подписанта, коммерческое предложение, тарифы, SLA и приложения к авиагрузовой операции. Незаполненные
значения остаются плейсхолдерами `{{...}}`; AWB, booking, рейс, аэропорты, цена, штрафы, лимиты ответственности
и сроки приемки не подставляются по образцу другого договора.

### 4. Текст шаблона

```
ДОГОВОР ПЕРЕВОЗКИ ГРУЗА (ОБЩИЙ ШАБЛОН)

г. {{city}}                                      {{contract_date}}

1. Стороны и полномочия
1.1. Сторона 1: {{party_1_name}}, представитель: {{party_1_representative}}.
1.2. Сторона 2: {{party_2_name}}, представитель: {{party_2_representative}}.
1.3. Полномочия подписантов подтверждаются уставом, доверенностью, решением органа управления или доверенностью
     на работу с авиагрузовыми документами.

2. Предмет и авиационные параметры
2.1. Предмет: авиаперевозка груза: booking, сдача в cargo terminal, terminal handling, security screening, AWB/MAWB/HAWB и выдача в аэропорту назначения.
2.2. Существенные параметры сделки:
- Номер договора: {{contract_number}}
- Дата договора: {{contract_date}}
- Наименование перевозчика: {{carrier_name}}
- Наименование грузоотправителя: {{shipper_name}}
- Описание груза: {{cargo_description}}
- Маршрут: {{route}}
- Вид транспорта: {{transport_mode}}
- Стоимость фрахта: {{freight_cost}}
- Срок доставки: {{delivery_deadline}}
- AWB/MAWB/HAWB: {{awb_number}}
- Booking reference: {{booking_ref}}
- Flight number: {{flight_number}}
- Аэропорт отправления: {{airport_departure}}
- Аэропорт назначения: {{airport_destination}}
- Cutoff time: {{cutoff_time}}
- Chargeable weight: {{chargeable_weight}}
2.3. В заявке или приложении указываются AWB/MAWB/HAWB или booking, flight number, airport of
     departure/destination, cutoff time, chargeable weight, terminal handling, ULD/pallet, customs/export
     control и special cargo requirements, если они применимы к операции.
2.4. Мультимодальное плечо допускается только как evidence к авиаперевозке: отдельный срок передачи в
     cargo terminal, акт handover и связь с AWB/booking.

3. Цена, сроки, SLA и приемка
3.1. Цена, валюта, freight/handling/storage charges, порядок оплаты и chargeable weight указываются по
     согласованным тарифам, rate sheet или коммерческому предложению.
3.2. Исполнение подтверждается: AWB/MAWB/HAWB, booking, flight manifest, warehouse receipt, акт терминала, фото, температурный лог и уведомление перевозчика.
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

- Владелец процесса проверяет профиль «авиаперевозка груза», стороны, authority matrix, коммерческие условия и
  evidence: booking, AWB/MAWB/HAWB, cargo manifest, flight status, terminal acceptance, weight note, special
  cargo approval.
- Срок первичной юридической проверки — 2 рабочих дня после получения полного комплекта; для dangerous goods,
  санкций, insurance gap или airport security срок фиксируется отдельно.
- Эскалация обязательна при событии: offload, missed cutoff, damage report, customs hold или отказ в приемке
  dangerous goods. Решение фиксируется в версии договора, приложении, протоколе разногласий или change log.
- Нельзя переносить AWB, flight number, airport pair, terminal status, customs status, chargeable weight или
  сумму из похожей сделки без первичного источника.

## Практический сценарий

- Сценарий: логистика согласует авиаперевозку с MAWB, booking, cutoff time и terminal handling до сдачи груза.
- Проверить: AWB/MAWB/HAWB, booking, flight number, аэропорты, cutoff time, ULD/pallet, chargeable weight, customs/export control и special cargo.
- Подтвердить источниками: AWB/MAWB/HAWB, booking, flight manifest, warehouse receipt, акт терминала, фото, температурный лог и уведомление перевозчика.
- Результат: проект содержит aviation-specific предмет, route/airport details, приемочные доказательства,
  liability cap, страхование, порядок претензий и ручную проверку special cargo/customs рисков.
- Предметная проверка: признаки «перевозка, груз, договор, перевозчик» используются только вместе с подтвержденными AWB/booking, приложениями и операционными документами.

## Правила ответа RAG-ассистента

- Использовать документ как источник типа «договор перевозки груза» по теме «Договор перевозки груза (общий шаблон)» только при совпадении запроса с авиагрузовым предметом документа.
- Перед ответом проверить: AWB/MAWB/HAWB, booking, flight number, аэропорты, cutoff time, ULD/pallet, chargeable weight, customs/export control и special cargo; полномочия подписантов, маршрут согласования, версию приложений и aviation evidence.
- Если нет AWB/booking, flight number, airport pair, cargo terminal status, цены, срока, акта приемки или
  ключевого факта, сначала вернуть уточняющие вопросы и не подставлять данные по догадке.
- Dangerous goods, temperature, customs/export control, санкции, валюту, страхование и cargo data передавать на
  ручную проверку.

## Доказательства и источники для ответа

- Профильные источники: booking, AWB/MAWB/HAWB, cargo manifest, flight status, terminal acceptance, weight note,
  special cargo approval.
- Корпоративные источники: заявка инициатора, карточка контрагента, authority matrix, коммерческое предложение,
  приложения, страховой или финансовый approval.
- Ограничение для ответа: перевозка описана без аэропортов, cutoff, chargeable weight, acceptance/release и
  special cargo. Если источник не подтверждает его, RAG-ответ указывает пробел и не подменяет его общей
  договорной нормой.
- Airport, flight, terminal, customs и dangerous goods используются как проверяемые факты: дата, статус, акт,
  разрешение, отметка или запрет.

## Типовые пользовательские запросы

| Запрос пользователя | Безопасная реакция ассистента |
|---------------------|-------------------------------|
| Подходит ли «Договор перевозки груза (общий шаблон)» для авиагрузовой сделки? | Сопоставить предмет, стороны, AWB/booking, аэропорты, SLA, special cargo и обязательные приложения; назвать недостающие факты и риски. |
| Сделай черновик договора. | Собрать поля; не выдумывать цену, рейс, AWB, cutoff time и реквизиты. |
| Документы для air cargo? | AWB, booking, invoice, packing list, акты, SLA, страхование, customs/export control. |
| Можно ли применить автоматически? | Проверить DG, temperature, customs/export control, sanctions и liability cap. |

## Ответственные роли

| Роль | Зона ответственности |
|------|----------------------|
| Руководитель юридического отдела | утверждает позицию по профилю «авиаперевозка груза», liability cap, waiver и нестандартные приложения |
| Air cargo operations manager | подтверждает operational facts: booking, AWB/MAWB/HAWB, cargo manifest, flight status, terminal acceptance, weight note, special cargo approval |
| Finance / insurance owner | сверяет тарифы, оплату, reserves, страховое покрытие, deductible и право регресса |
| Compliance / customs contact | проверяет для «Договор перевозки груза (общий шаблон)» sanctions/export control, dangerous goods, airport security и ограничения передачи данных |

## Риски и ограничения

- Нельзя готовить договор или RAG-ответ без evidence по профилю «авиаперевозка груза»: booking, AWB/MAWB/HAWB,
  cargo manifest, flight status, terminal acceptance, weight note, special cargo approval.
- Ключевой риск сценария: перевозка описана без аэропортов, cutoff, chargeable weight, acceptance/release и
  special cargo.
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

- ГК РФ, глава 40 (перевозка)
- ФЗ от 08.11.2007 № 259-ФЗ

## Критерии качества ответа

- ответ решает именно сценарий «авиаперевозка груза» и не смешивает его со смежным договором или претензией
- источники подтверждения названы предметно: booking, AWB/MAWB/HAWB, cargo manifest, flight status, terminal
  acceptance, weight note, special cargo approval
- учтен профильный риск: перевозка описана без аэропортов, cutoff, chargeable weight, acceptance/release и
  special cargo
- если airport, flight, terminal, customs или dangerous goods не подтверждены документом, ответ запрашивает
  источник и не делает вывод по аналогии

## Контрольный список

- [ ] запрос сопоставлен с документом «Договор перевозки груза (общий шаблон)» и профилем «авиаперевозка груза»
- [ ] собраны профильные evidence: booking, AWB/MAWB/HAWB, cargo manifest, flight status, terminal acceptance,
  weight note, special cargo approval
- [ ] проверены полномочия подписанта, версия приложений, liability cap, insurance и payment terms
- [ ] оценено ограничение: перевозка описана без аэропортов, cutoff, chargeable weight, acceptance/release и
  special cargo
- [ ] customs/export control, dangerous goods, temperature или security условия включены только при
  подтвержденной применимости

## Порядок пересмотра и актуализации

Владелец документа: Руководитель юридического отдела. Плановый пересмотр проводится не реже одного раза в 12
месяцев.

Внеплановый пересмотр нужен после события: offload, missed cutoff, damage report, customs hold или отказ в
приемке dangerous goods; также после изменения carrier/GHA rules, airport security требований, customs/export
control режима, страхового покрытия или судебной практики.

При пересмотре Legal выборочно сверяет 3-5 завершенных кейсов профиля «авиаперевозка груза» и обновляет evidence
list, сроки согласования, роли эскалации и ограничения RAG-ответа.

## История изменений

| Версия | Дата | Изменение | Автор |
|--------|------|-----------|-------|
| 1.0 | 2026-05-15 | Первичная редакция внутреннего документа | Владелец процесса |

> Применять «Договор перевозки груза (общий шаблон)» после подтверждения владельцем процесса; спорные и нетиповые кейсы требуют ручной проверки.
