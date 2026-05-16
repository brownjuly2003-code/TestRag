---
doc_id: legal_contract_rent_warehouse
title: Договор аренды складских помещений
category: Legal contract templates
document_type: договор
department: Legal
synthetic_demo: false
source_type: internal_controlled
version: "1.0"
effective_date: '2026-05-15'
owner_role: Руководитель юридического отдела
related_normative_sources:
- ГК РФ, глава 34 (аренда)
- ГК РФ, ст. 621 (договор аренды)
keywords:
- аренда склада
- склад
- температурный режим
confidentiality: internal
---

# Договор аренды складских помещений

## Назначение

Договор аренды складских помещений используется для сценария: арендуется зона хранения авиагруза до acceptance
или после arrival/release. Это рабочий шаблон Legal для авиагрузовой сделки, где предмет проверяется по
источникам, а не по названию документа.

До выпуска проекта юрист сверяет полномочия, приложения, лимиты ответственности, страхование и доказательства:
lease plan, temperature map, terminal rules, acceptance act, storage tariff, access log, cargo segregation
records. AWB/MAWB/HAWB, airport, flight, terminal, customs и dangerous goods указываются только как условия или
ограничения.

## Область применения

Документ применяется, когда запрос связан с профилем «аренда склада или cold room у cargo terminal» и есть
операционная связка с air cargo route, terminal handover или расчетами по перевозке.

Наземная передача упоминается только как проверяемое evidence: pickup/delivery proof, terminal slot, пломбы или
temperature log, если они действительно входят в сделку. Customs/export control, dangerous goods, temperature
cargo и security screening включаются только при подтвержденной применимости.

## Термины

- **Аренда склада или cold room у cargo terminal** — профиль документа, который определяет обязательные
  приложения и evidence.
- **Aviation evidence по сделке** — lease plan, temperature map, terminal rules, acceptance act, storage tariff,
  access log, cargo segregation records; комплект подтверждает предмет, цену, сроки, приемку и пределы
  ответственности.
- **Операционное ограничение** — складская зона не покрывает temperature mapping, security, dangerous goods
  segregation или terminal handover; условие выносится в приложение, SLA или протокол разногласий.
- **Эскалационное событие** — temperature excursion, access breach, storage overrun или спор о состоянии груза;
  после него проект возвращается к Legal, operations и finance/insurance.

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
| `landlord_name` | Наименование арендодателя | `{{landlord_name}}` |
| `tenant_name` | Наименование арендатора | `{{tenant_name}}` |
| `warehouse_address` | Адрес склада | `{{warehouse_address}}` |
| `area_sqm` | Площади кв. м | `{{area_sqm}}` |
| `rent_amount` | Размер арендной платы | `{{rent_amount}}` |
| `temperature_regime` | Температуры режима | `{{temperature_regime}}` |
| `security_terms` | Условия безопасности | `{{security_terms}}` |
| `terminal_zone` | Зона cargo terminal/СВХ | `{{terminal_zone}}` |
| `airport_pass_rules` | Airport pass/access rules | `{{airport_pass_rules}}` |
| `storage_condition` | Температурный/DG режим | `{{storage_condition}}` |
| `warehouse_receipt_ref` | Warehouse receipt | `{{warehouse_receipt_ref}}` |
| `handling_sla` | Terminal handling SLA | `{{handling_sla}}` |

### 3. Подготовка текста

Ответственный юрист сверяет каждое поле с первичными источниками: заявку инициатора, карточку контрагента,
полномочия подписанта, коммерческое предложение, тарифы, SLA и приложения к авиагрузовой операции. Незаполненные
значения остаются плейсхолдерами `{{...}}`; AWB, booking, рейс, аэропорты, цена, штрафы, лимиты ответственности
и сроки приемки не подставляются по образцу другого договора.

### 4. Текст шаблона

```
ДОГОВОР АРЕНДЫ СКЛАДСКИХ ПОМЕЩЕНИЙ

г. {{city}}                                      {{contract_date}}

1. Стороны и полномочия
1.1. Сторона 1: {{party_1_name}}, представитель: {{party_1_representative}}.
1.2. Сторона 2: {{party_2_name}}, представитель: {{party_2_representative}}.
1.3. Полномочия подписантов подтверждаются уставом, доверенностью, решением органа управления или доверенностью
     на работу с авиагрузовыми документами.

2. Предмет и авиационные параметры
2.1. Предмет: аренда, storage или эксплуатация зоны грузового терминала/СВХ для приемки, хранения, обработки,
     комплектации и выдачи авиагрузов.
2.2. Существенные параметры сделки:
- Номер договора: {{contract_number}}
- Дата договора: {{contract_date}}
- Наименование арендодателя: {{landlord_name}}
- Наименование арендатора: {{tenant_name}}
- Адрес склада: {{warehouse_address}}
- Площади кв. м: {{area_sqm}}
- Размер арендной платы: {{rent_amount}}
- Температуры режима: {{temperature_regime}}
- Условия безопасности: {{security_terms}}
- Зона cargo terminal/СВХ: {{terminal_zone}}
- Airport pass/access rules: {{airport_pass_rules}}
- Температурный/DG режим: {{storage_condition}}
- Warehouse receipt: {{warehouse_receipt_ref}}
- Terminal handling SLA: {{handling_sla}}
2.3. В заявке или приложении указываются AWB/MAWB/HAWB или booking, flight number, airport of
     departure/destination, cutoff time, chargeable weight, terminal handling, ULD/pallet, customs/export
     control и special cargo requirements, если они применимы к операции.
2.4. Передача груза в аэропорт или из него описывается только при наличии pickup/delivery proof,
     terminal slot, пломб, temperature log или иного handover evidence, связанного с
     AWB/booking.

3. Цена, сроки, SLA и приемка
3.1. Цена, валюта, freight/handling/storage charges, порядок оплаты и chargeable weight указываются по
     согласованным тарифам, rate sheet или коммерческому предложению.
3.2. Исполнение подтверждается: договор аренды/хранения, план зоны, warehouse receipt, журнал доступа,
     температурные логи, акты повреждения/недостачи и отчеты handling.
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

- Владелец процесса проверяет профиль «аренда склада или cold room у cargo terminal», стороны, authority matrix,
  коммерческие условия и evidence: lease plan, temperature map, terminal rules, acceptance act, storage tariff,
  access log, cargo segregation records.
- Срок первичной юридической проверки — 2 рабочих дня после получения полного комплекта; для dangerous goods,
  санкций, insurance gap или airport security срок фиксируется отдельно.
- Эскалация обязательна при событии: temperature excursion, access breach, storage overrun или спор о состоянии
  груза. Решение фиксируется в версии договора, приложении, протоколе разногласий или change log.
- Нельзя переносить AWB, flight number, airport pair, terminal status, customs status, chargeable weight или
  сумму из похожей сделки без первичного источника.

## Практический сценарий

- Сценарий: компания арендует температурную зону в cargo terminal для pharma cargo между arrival и customs clearance.
- Проверить: адрес и зону терминала, допуск, storage condition, airport security, акты приемки, temperature/DG
  requirements, ответственность и insurance.
- Подтвердить источниками: договор аренды/хранения, план зоны, warehouse receipt, журнал доступа, температурные
  логи, акты повреждения/недостачи и отчеты handling.
- Результат: проект содержит aviation-specific предмет, route/airport details, приемочные доказательства,
  liability cap, страхование, порядок претензий и ручную проверку special cargo/customs рисков.
- Предметная проверка: признаки «аренда склада, склад, температурный режим» используются только вместе с подтвержденными AWB/booking, приложениями и операционными документами.

## Правила ответа RAG-ассистента

- Использовать документ как источник типа «договор» по теме «Договор аренды складских помещений» только при совпадении запроса с авиагрузовым предметом документа.
- Перед ответом проверить: адрес и зону терминала, допуск, storage condition, airport security, акты приемки,
  temperature/DG requirements, ответственность и insurance; полномочия подписантов, маршрут согласования, версию
  приложений и aviation evidence.
- Если нет AWB/booking, flight number, airport pair, cargo terminal status, цены, срока, акта приемки или
  ключевого факта, сначала вернуть уточняющие вопросы и не подставлять данные по догадке.
- Dangerous goods, temperature, customs/export control, санкции, валюту, страхование и cargo data передавать на
  ручную проверку.

## Доказательства и источники для ответа

- Профильные источники: lease plan, temperature map, terminal rules, acceptance act, storage tariff, access log,
  cargo segregation records.
- Корпоративные источники: заявка инициатора, карточка контрагента, authority matrix, коммерческое предложение,
  приложения, страховой или финансовый approval.
- Ограничение для ответа: складская зона не покрывает temperature mapping, security, dangerous goods segregation
  или terminal handover. Если источник не подтверждает его, RAG-ответ указывает пробел и не подменяет его общей
  договорной нормой.
- Airport, flight, terminal, customs и dangerous goods используются как проверяемые факты: дата, статус, акт,
  разрешение, отметка или запрет.

## Типовые пользовательские запросы

| Запрос пользователя | Безопасная реакция ассистента |
|---------------------|-------------------------------|
| Подходит ли «Договор аренды складских помещений» для авиагрузовой сделки? | Сопоставить предмет, стороны, AWB/booking, аэропорты, SLA, special cargo и обязательные приложения; назвать недостающие факты и риски. |
| Сделай черновик договора. | Собрать поля; не выдумывать цену, рейс, AWB, cutoff time и реквизиты. |
| Документы для air cargo? | AWB, booking, invoice, packing list, акты, SLA, страхование, customs/export control. |
| Можно ли применить автоматически? | Проверить DG, temperature, customs/export control, sanctions и liability cap. |

## Ответственные роли

| Роль | Зона ответственности |
|------|----------------------|
| Руководитель юридического отдела | утверждает позицию по профилю «аренда склада или cold room у cargo terminal», liability cap, waiver и нестандартные приложения |
| Warehouse lease owner | подтверждает operational facts: lease plan, temperature map, terminal rules, acceptance act, storage tariff, access log, cargo segregation records |
| Finance / insurance owner | сверяет тарифы, оплату, reserves, страховое покрытие, deductible и право регресса |
| Compliance / customs contact | проверяет для «Договор аренды складских помещений» sanctions/export control, dangerous goods, airport security и ограничения передачи данных |

## Риски и ограничения

- Нельзя готовить договор или RAG-ответ без evidence по профилю «аренда склада или cold room у cargo terminal»:
  lease plan, temperature map, terminal rules, acceptance act, storage tariff, access log, cargo segregation
  records.
- Ключевой риск сценария: складская зона не покрывает temperature mapping, security, dangerous goods segregation
  или terminal handover.
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

- ГК РФ, глава 34 (аренда)
- ГК РФ, ст. 621 (договор аренды)

## Критерии качества ответа

- ответ решает именно сценарий «аренда склада или cold room у cargo terminal» и не смешивает его со смежным
  договором или претензией
- источники подтверждения названы предметно: lease plan, temperature map, terminal rules, acceptance act,
  storage tariff, access log, cargo segregation records
- учтен профильный риск: складская зона не покрывает temperature mapping, security, dangerous goods segregation
  или terminal handover
- если airport, flight, terminal, customs или dangerous goods не подтверждены документом, ответ запрашивает
  источник и не делает вывод по аналогии

## Контрольный список

- [ ] запрос сопоставлен с документом «Договор аренды складских помещений» и профилем «аренда склада или cold
  room у cargo terminal»
- [ ] собраны профильные evidence: lease plan, temperature map, terminal rules, acceptance act, storage tariff,
  access log, cargo segregation records
- [ ] проверены полномочия подписанта, версия приложений, liability cap, insurance и payment terms
- [ ] оценено ограничение: складская зона не покрывает temperature mapping, security, dangerous goods
  segregation или terminal handover
- [ ] customs/export control, dangerous goods, temperature или security условия включены только при
  подтвержденной применимости

## Порядок пересмотра и актуализации

Владелец документа: Руководитель юридического отдела. Плановый пересмотр проводится не реже одного раза в 12
месяцев.

Внеплановый пересмотр нужен после события: temperature excursion, access breach, storage overrun или спор о
состоянии груза; также после изменения carrier/GHA rules, airport security требований, customs/export control
режима, страхового покрытия или судебной практики.

При пересмотре Legal выборочно сверяет 3-5 завершенных кейсов профиля «аренда склада или cold room у cargo
terminal» и обновляет evidence list, сроки согласования, роли эскалации и ограничения RAG-ответа.

## История изменений

| Версия | Дата | Изменение | Автор |
|--------|------|-----------|-------|
| 1.0 | 2026-05-15 | Первичная редакция внутреннего документа | Владелец процесса |

> Применять «Договор аренды складских помещений» после подтверждения владельцем процесса; спорные и нетиповые кейсы требуют ручной проверки.
