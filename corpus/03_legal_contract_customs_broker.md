---
doc_id: legal_contract_customs_broker
title: Договор с таможенным брокером
category: Legal contract templates
document_type: договор оказания услуг
department: Legal
synthetic_demo: false
source_type: internal_controlled
version: "1.0"
effective_date: '2026-05-15'
owner_role: Руководитель юридического отдела
related_normative_sources:
- ТК ВЭД (Таможенный кодекс ЕАЭС)
- ФЗ от 03.08.2018 № 289-ФЗ (о таможенном регулировании)
keywords:
- таможенный брокер
- декларирование
- ТК ВЭД
confidentiality: internal
---

# Договор с таможенным брокером

## Назначение

Договор с таможенным брокером используется для сценария: customs broker оформляет декларацию, разрешения и
ответы таможне по air cargo shipment. Это рабочий шаблон Legal для авиагрузовой сделки, где предмет проверяется
по источникам, а не по названию документа.

До выпуска проекта юрист сверяет полномочия, приложения, лимиты ответственности, страхование и доказательства:
invoice, packing list, AWB/MAWB/HAWB, cargo manifest, customs declaration, permits, broker authority, customs
messages. AWB/MAWB/HAWB, airport, flight, terminal, customs и dangerous goods указываются только как условия или
ограничения.

## Область применения

Документ применяется, когда запрос связан с профилем «таможенное оформление авиагруза» и есть операционная
связка с air cargo route, terminal handover или расчетами по перевозке.

Наземная передача упоминается только как проверяемое evidence: pickup/delivery proof, terminal slot, пломбы или
temperature log, если они действительно входят в сделку. Customs/export control, dangerous goods, temperature
cargo и security screening включаются только при подтвержденной применимости.

## Термины

- **Таможенное оформление авиагруза** — профиль документа, который определяет обязательные приложения и
  evidence.
- **Aviation evidence по сделке** — invoice, packing list, AWB/MAWB/HAWB, cargo manifest, customs declaration,
  permits, broker authority, customs messages; комплект подтверждает предмет, цену, сроки, приемку и пределы
  ответственности.
- **Операционное ограничение** — декларирование идет без полномочий, кодов ТН ВЭД, export control проверки или
  terminal release; условие выносится в приложение, SLA или протокол разногласий.
- **Эскалационное событие** — customs hold, request for documents, inspection, sanctions hit или корректировка
  таможенной стоимости; после него проект возвращается к Legal, operations и finance/insurance.

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
| `broker_name` | Наименование брокера | `{{broker_name}}` |
| `client_name` | Наименование клиента | `{{client_name}}` |
| `customs_procedure` | Порядок таможенного | `{{customs_procedure}}` |
| `fee_structure` | Структура вознаграждения | `{{fee_structure}}` |
| `cargo_description` | Описание груза | `{{cargo_description}}` |
| `customs_code` | Код ТН ВЭД | `{{customs_code}}` |
| `awb_mawb_hawb` | AWB/MAWB/HAWB | `{{awb_mawb_hawb}}` |
| `flight_number` | Flight number | `{{flight_number}}` |
| `customs_declaration_ref` | Номер декларации | `{{customs_declaration_ref}}` |
| `export_control_status` | Статус export control | `{{export_control_status}}` |
| `terminal_hold_terms` | Условия terminal hold | `{{terminal_hold_terms}}` |

### 3. Подготовка текста

Ответственный юрист сверяет каждое поле с первичными источниками: заявку инициатора, карточку контрагента,
полномочия подписанта, коммерческое предложение, тарифы, SLA и приложения к авиагрузовой операции. Незаполненные
значения остаются плейсхолдерами `{{...}}`; AWB, booking, рейс, аэропорты, цена, штрафы, лимиты ответственности
и сроки приемки не подставляются по образцу другого договора.

### 4. Текст шаблона

```
ДОГОВОР С ТАМОЖЕННЫМ БРОКЕРОМ

г. {{city}}                                      {{contract_date}}

1. Стороны и полномочия
1.1. Сторона 1: {{party_1_name}}, представитель: {{party_1_representative}}.
1.2. Сторона 2: {{party_2_name}}, представитель: {{party_2_representative}}.
1.3. Полномочия подписантов подтверждаются уставом, доверенностью, решением органа управления или доверенностью
     на работу с авиагрузовыми документами.

2. Предмет и авиационные параметры
2.1. Предмет: таможенное оформление авиагруза, export control, санкционная проверка, взаимодействие с терминалом и авиаперевозчиком.
2.2. Существенные параметры сделки:
- Номер договора: {{contract_number}}
- Дата договора: {{contract_date}}
- Наименование брокера: {{broker_name}}
- Наименование клиента: {{client_name}}
- Порядок таможенного: {{customs_procedure}}
- Структура вознаграждения: {{fee_structure}}
- Описание груза: {{cargo_description}}
- Код ТН ВЭД: {{customs_code}}
- AWB/MAWB/HAWB: {{awb_mawb_hawb}}
- Flight number: {{flight_number}}
- Номер декларации: {{customs_declaration_ref}}
- Статус export control: {{export_control_status}}
- Условия terminal hold: {{terminal_hold_terms}}
2.3. В заявке или приложении указываются AWB/MAWB/HAWB или booking, flight number, airport of
     departure/destination, cutoff time, chargeable weight, terminal handling, ULD/pallet, customs/export
     control и special cargo requirements, если они применимы к операции.
2.4. Передача груза в аэропорт или из него описывается только при наличии pickup/delivery proof,
     terminal slot, пломб, temperature log или иного handover evidence, связанного с
     AWB/booking.

3. Цена, сроки, SLA и приемка
3.1. Цена, валюта, freight/handling/storage charges, порядок оплаты и chargeable weight указываются по
     согласованным тарифам, rate sheet или коммерческому предложению.
3.2. Исполнение подтверждается: AWB/MAWB/HAWB, invoice, packing list, декларация, разрешения, export control memo, акт досмотра и уведомления терминала.
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

- Владелец процесса проверяет профиль «таможенное оформление авиагруза», стороны, authority matrix, коммерческие
  условия и evidence: invoice, packing list, AWB/MAWB/HAWB, cargo manifest, customs declaration, permits, broker
  authority, customs messages.
- Срок первичной юридической проверки — 2 рабочих дня после получения полного комплекта; для dangerous goods,
  санкций, insurance gap или airport security срок фиксируется отдельно.
- Эскалация обязательна при событии: customs hold, request for documents, inspection, sanctions hit или
  корректировка таможенной стоимости. Решение фиксируется в версии договора, приложении, протоколе разногласий
  или change log.
- Нельзя переносить AWB, flight number, airport pair, terminal status, customs status, chargeable weight или
  сумму из похожей сделки без первичного источника.

## Практический сценарий

- Сценарий: брокер оформляет экспортный авиагруз с lithium batteries до cutoff time терминала.
- Проверить: код ТН ВЭД, AWB, рейс, аэропорты, разрешения, dangerous goods, sanctions, temperature и terminal hold.
- Подтвердить источниками: AWB/MAWB/HAWB, invoice, packing list, декларация, разрешения, export control memo, акт досмотра и уведомления терминала.
- Результат: проект содержит aviation-specific предмет, route/airport details, приемочные доказательства,
  liability cap, страхование, порядок претензий и ручную проверку special cargo/customs рисков.
- Предметная проверка: признаки «таможенный брокер, декларирование, ТК ВЭД» используются только вместе с подтвержденными AWB/booking, приложениями и операционными документами.

## Правила ответа RAG-ассистента

- Использовать документ как источник типа «договор оказания услуг» по теме «Договор с таможенным брокером» только при совпадении запроса с авиагрузовым предметом документа.
- Перед ответом проверить: код ТН ВЭД, AWB, рейс, аэропорты, разрешения, dangerous goods, sanctions, temperature и terminal hold; полномочия подписантов, маршрут согласования, версию приложений и aviation evidence.
- Если нет AWB/booking, flight number, airport pair, cargo terminal status, цены, срока, акта приемки или
  ключевого факта, сначала вернуть уточняющие вопросы и не подставлять данные по догадке.
- Dangerous goods, temperature, customs/export control, санкции, валюту, страхование и cargo data передавать на
  ручную проверку.

## Доказательства и источники для ответа

- Профильные источники: invoice, packing list, AWB/MAWB/HAWB, cargo manifest, customs declaration, permits,
  broker authority, customs messages.
- Корпоративные источники: заявка инициатора, карточка контрагента, authority matrix, коммерческое предложение,
  приложения, страховой или финансовый approval.
- Ограничение для ответа: декларирование идет без полномочий, кодов ТН ВЭД, export control проверки или terminal
  release. Если источник не подтверждает его, RAG-ответ указывает пробел и не подменяет его общей договорной
  нормой.
- Airport, flight, terminal, customs и dangerous goods используются как проверяемые факты: дата, статус, акт,
  разрешение, отметка или запрет.

## Типовые пользовательские запросы

| Запрос пользователя | Безопасная реакция ассистента |
|---------------------|-------------------------------|
| Подходит ли «Договор с таможенным брокером» для авиагрузовой сделки? | Сопоставить предмет, стороны, AWB/booking, аэропорты, SLA, special cargo и обязательные приложения; назвать недостающие факты и риски. |
| Сделай черновик договора. | Собрать поля; не выдумывать цену, рейс, AWB, cutoff time и реквизиты. |
| Документы для air cargo? | AWB, booking, invoice, packing list, акты, SLA, страхование, customs/export control. |
| Можно ли применить автоматически? | Проверить DG, temperature, customs/export control, sanctions и liability cap. |

## Ответственные роли

| Роль | Зона ответственности |
|------|----------------------|
| Руководитель юридического отдела | утверждает позицию по профилю «таможенное оформление авиагруза», liability cap, waiver и нестандартные приложения |
| Customs clearance lead | подтверждает operational facts: invoice, packing list, AWB/MAWB/HAWB, cargo manifest, customs declaration, permits, broker authority, customs messages |
| Finance / insurance owner | сверяет тарифы, оплату, reserves, страховое покрытие, deductible и право регресса |
| Compliance / customs contact | проверяет для «Договор с таможенным брокером» sanctions/export control, dangerous goods, airport security и ограничения передачи данных |

## Риски и ограничения

- Нельзя готовить договор или RAG-ответ без evidence по профилю «таможенное оформление авиагруза»: invoice,
  packing list, AWB/MAWB/HAWB, cargo manifest, customs declaration, permits, broker authority, customs messages.
- Ключевой риск сценария: декларирование идет без полномочий, кодов ТН ВЭД, export control проверки или terminal
  release.
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

- ТК ВЭД (Таможенный кодекс ЕАЭС)
- ФЗ от 03.08.2018 № 289-ФЗ (о таможенном регулировании)

## Критерии качества ответа

- ответ решает именно сценарий «таможенное оформление авиагруза» и не смешивает его со смежным договором или
  претензией
- источники подтверждения названы предметно: invoice, packing list, AWB/MAWB/HAWB, cargo manifest, customs
  declaration, permits, broker authority, customs messages
- учтен профильный риск: декларирование идет без полномочий, кодов ТН ВЭД, export control проверки или terminal
  release
- если airport, flight, terminal, customs или dangerous goods не подтверждены документом, ответ запрашивает
  источник и не делает вывод по аналогии

## Контрольный список

- [ ] запрос сопоставлен с документом «Договор с таможенным брокером» и профилем «таможенное оформление
  авиагруза»
- [ ] собраны профильные evidence: invoice, packing list, AWB/MAWB/HAWB, cargo manifest, customs declaration,
  permits, broker authority, customs messages
- [ ] проверены полномочия подписанта, версия приложений, liability cap, insurance и payment terms
- [ ] оценено ограничение: декларирование идет без полномочий, кодов ТН ВЭД, export control проверки или
  terminal release
- [ ] customs/export control, dangerous goods, temperature или security условия включены только при
  подтвержденной применимости

## Порядок пересмотра и актуализации

Владелец документа: Руководитель юридического отдела. Плановый пересмотр проводится не реже одного раза в 12
месяцев.

Внеплановый пересмотр нужен после события: customs hold, request for documents, inspection, sanctions hit или
корректировка таможенной стоимости; также после изменения carrier/GHA rules, airport security требований,
customs/export control режима, страхового покрытия или судебной практики.

При пересмотре Legal выборочно сверяет 3-5 завершенных кейсов профиля «таможенное оформление авиагруза» и
обновляет evidence list, сроки согласования, роли эскалации и ограничения RAG-ответа.

## История изменений

| Версия | Дата | Изменение | Автор |
|--------|------|-----------|-------|
| 1.0 | 2026-05-15 | Первичная редакция внутреннего документа | Владелец процесса |

> Применять «Договор с таможенным брокером» после подтверждения владельцем процесса; спорные и нетиповые кейсы требуют ручной проверки.
