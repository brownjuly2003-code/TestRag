---
doc_id: legal_contract_supply_goods
title: Договор поставки товаров (общий шаблон)
category: Legal contract templates
document_type: договор поставки
department: Legal
synthetic_demo: false
source_type: internal_controlled
version: "1.0"
effective_date: '2026-05-15'
owner_role: Руководитель юридического отдела
related_normative_sources:
- ГК РФ, глава 30 (поставка)
- ГК РФ, ст. 506-524 (договор поставки)
keywords:
- поставка
- договор
- инкотермс
- приемка
confidentiality: internal
---

# Договор поставки товаров (общий шаблон)

## Назначение

Договор поставки товаров (общий шаблон) используется для сценария: поставляются пломбы, labels, термоконтейнеры,
упаковка и расходные материалы для terminal handling. Это рабочий шаблон Legal для авиагрузовой сделки, где
предмет проверяется по источникам, а не по названию документа.

До выпуска проекта юрист сверяет полномочия, приложения, лимиты ответственности, страхование и доказательства:
purchase order, specs, certificates, batch list, delivery note, acceptance act, photos, nonconformity report.
AWB/MAWB/HAWB, airport, flight, terminal, customs и dangerous goods указываются только как условия или
ограничения.

## Область применения

Документ применяется, когда запрос связан с профилем «поставка упаковки и расходников для авиагруза» и есть
операционная связка с air cargo route, terminal handover или расчетами по перевозке.

Наземная передача упоминается только как проверяемое evidence: pickup/delivery proof, terminal slot, пломбы или
temperature log, если они действительно входят в сделку. Customs/export control, dangerous goods, temperature
cargo и security screening включаются только при подтвержденной применимости.

## Термины

- **Поставка упаковки и расходников для авиагруза** — профиль документа, который определяет обязательные
  приложения и evidence.
- **Aviation evidence по сделке** — purchase order, specs, certificates, batch list, delivery note, acceptance
  act, photos, nonconformity report; комплект подтверждает предмет, цену, сроки, приемку и пределы
  ответственности.
- **Операционное ограничение** — товары не подходят для screening, temperature control, dangerous goods marking
  или airline acceptance; условие выносится в приложение, SLA или протокол разногласий.
- **Эскалационное событие** — defective packaging, wrong labels, shortage before cutoff или rejected shipment;
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
| `supplier_name` | Наименование поставщика | `{{supplier_name}}` |
| `buyer_name` | Покупатель | `{{buyer_name}}` |
| `goods_description` | Описание товаров | `{{goods_description}}` |
| `quantity` | Количество | `{{quantity}}` |
| `price` | Цена | `{{price}}` |
| `delivery_terms` | Условия доставки | `{{delivery_terms}}` |
| `incoterms` | Incoterms | `{{incoterms}}` |
| `penalty_rate` | Ставка штрафа | `{{penalty_rate}}` |
| `aviation_use_scope` | Назначение для air cargo/GSE | `{{aviation_use_scope}}` |
| `certificate_package` | Сертификаты/SDS | `{{certificate_package}}` |
| `terminal_delivery_point` | Место поставки cargo terminal | `{{terminal_delivery_point}}` |
| `acceptance_test` | Приемочные испытания | `{{acceptance_test}}` |
| `criticality_level` | Критичность для SLA | `{{criticality_level}}` |

### 3. Подготовка текста

Ответственный юрист сверяет каждое поле с первичными источниками: заявку инициатора, карточку контрагента,
полномочия подписанта, коммерческое предложение, тарифы, SLA и приложения к авиагрузовой операции. Незаполненные
значения остаются плейсхолдерами `{{...}}`; AWB, booking, рейс, аэропорты, цена, штрафы, лимиты ответственности
и сроки приемки не подставляются по образцу другого договора.

### 4. Текст шаблона

```
ДОГОВОР ПОСТАВКИ ТОВАРОВ (ОБЩИЙ ШАБЛОН)

г. {{city}}                                      {{contract_date}}

1. Стороны и полномочия
1.1. Сторона 1: {{party_1_name}}, представитель: {{party_1_representative}}.
1.2. Сторона 2: {{party_2_name}}, представитель: {{party_2_representative}}.
1.3. Полномочия подписантов подтверждаются уставом, доверенностью, решением органа управления или доверенностью
     на работу с авиагрузовыми документами.

2. Предмет и авиационные параметры
2.1. Предмет: поставка или лизинг для авиационного грузового контура: equipment, GSE, terminal supplies,
     упаковка, пломбы, ULD accessories, cold chain материалы, ГСМ или запчасти.
2.2. Существенные параметры сделки:
- Номер договора: {{contract_number}}
- Дата договора: {{contract_date}}
- Наименование поставщика: {{supplier_name}}
- Покупатель: {{buyer_name}}
- Описание товаров: {{goods_description}}
- Количество: {{quantity}}
- Цена: {{price}}
- Условия доставки: {{delivery_terms}}
- Incoterms: {{incoterms}}
- Ставка штрафа: {{penalty_rate}}
- Назначение для air cargo/GSE: {{aviation_use_scope}}
- Сертификаты/SDS: {{certificate_package}}
- Место поставки cargo terminal: {{terminal_delivery_point}}
- Приемочные испытания: {{acceptance_test}}
- Критичность для SLA: {{criticality_level}}
2.3. В заявке или приложении указываются AWB/MAWB/HAWB или booking, flight number, airport of
     departure/destination, cutoff time, chargeable weight, terminal handling, ULD/pallet, customs/export
     control и special cargo requirements, если они применимы к операции.
2.4. Передача груза в аэропорт или из него описывается только при наличии pickup/delivery proof,
     terminal slot, пломб, temperature log или иного handover evidence, связанного с
     AWB/booking.

3. Цена, сроки, SLA и приемка
3.1. Цена, валюта, freight/handling/storage charges, порядок оплаты и chargeable weight указываются по
     согласованным тарифам, rate sheet или коммерческому предложению.
3.2. Исполнение подтверждается: спецификация, сертификаты, SDS, УПД/накладная, акт приемки, фото, результаты
     испытаний, warehouse receipt и претензионный акт.
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

- Владелец процесса проверяет профиль «поставка упаковки и расходников для авиагруза», стороны, authority
  matrix, коммерческие условия и evidence: purchase order, specs, certificates, batch list, delivery note,
  acceptance act, photos, nonconformity report.
- Срок первичной юридической проверки — 2 рабочих дня после получения полного комплекта; для dangerous goods,
  санкций, insurance gap или airport security срок фиксируется отдельно.
- Эскалация обязательна при событии: defective packaging, wrong labels, shortage before cutoff или rejected
  shipment. Решение фиксируется в версии договора, приложении, протоколе разногласий или change log.
- Нельзя переносить AWB, flight number, airport pair, terminal status, customs status, chargeable weight или
  сумму из похожей сделки без первичного источника.

## Практический сценарий

- Сценарий: закупка принимает оборудование для pallet build-up и проверяет сертификаты, испытания и влияние на
  терминальный SLA.
- Проверить: номенклатуру, aviation use, сертификаты, срок поставки, terminal delivery point, испытания,
  безопасность и влияние на SLA.
- Подтвердить источниками: спецификация, сертификаты, SDS, УПД/накладная, акт приемки, фото, результаты
  испытаний, warehouse receipt и претензионный акт.
- Результат: проект содержит aviation-specific предмет, route/airport details, приемочные доказательства,
  liability cap, страхование, порядок претензий и ручную проверку special cargo/customs рисков.
- Предметная проверка: признаки «поставка, договор, инкотермс, приемка» используются только вместе с подтвержденными AWB/booking, приложениями и операционными документами.

## Правила ответа RAG-ассистента

- Использовать документ как источник типа «договор поставки» по теме «Договор поставки товаров (общий шаблон)» только при совпадении запроса с авиагрузовым предметом документа.
- Перед ответом проверить: номенклатуру, aviation use, сертификаты, срок поставки, terminal delivery point,
  испытания, безопасность и влияние на SLA; полномочия подписантов, маршрут согласования, версию приложений и
  aviation evidence.
- Если нет AWB/booking, flight number, airport pair, cargo terminal status, цены, срока, акта приемки или
  ключевого факта, сначала вернуть уточняющие вопросы и не подставлять данные по догадке.
- Dangerous goods, temperature, customs/export control, санкции, валюту, страхование и cargo data передавать на
  ручную проверку.

## Доказательства и источники для ответа

- Профильные источники: purchase order, specs, certificates, batch list, delivery note, acceptance act, photos,
  nonconformity report.
- Корпоративные источники: заявка инициатора, карточка контрагента, authority matrix, коммерческое предложение,
  приложения, страховой или финансовый approval.
- Ограничение для ответа: товары не подходят для screening, temperature control, dangerous goods marking или
  airline acceptance. Если источник не подтверждает его, RAG-ответ указывает пробел и не подменяет его общей
  договорной нормой.
- Airport, flight, terminal, customs и dangerous goods используются как проверяемые факты: дата, статус, акт,
  разрешение, отметка или запрет.

## Типовые пользовательские запросы

| Запрос пользователя | Безопасная реакция ассистента |
|---------------------|-------------------------------|
| Подходит ли «Договор поставки товаров (общий шаблон)» для авиагрузовой сделки? | Сопоставить предмет, стороны, AWB/booking, аэропорты, SLA, special cargo и обязательные приложения; назвать недостающие факты и риски. |
| Сделай черновик договора. | Собрать поля; не выдумывать цену, рейс, AWB, cutoff time и реквизиты. |
| Документы для air cargo? | AWB, booking, invoice, packing list, акты, SLA, страхование, customs/export control. |
| Можно ли применить автоматически? | Проверить DG, temperature, customs/export control, sanctions и liability cap. |

## Ответственные роли

| Роль | Зона ответственности |
|------|----------------------|
| Руководитель юридического отдела | утверждает позицию по профилю «поставка упаковки и расходников для авиагруза», liability cap, waiver и нестандартные приложения |
| Cargo supplies owner | подтверждает operational facts: purchase order, specs, certificates, batch list, delivery note, acceptance act, photos, nonconformity report |
| Finance / insurance owner | сверяет тарифы, оплату, reserves, страховое покрытие, deductible и право регресса |
| Compliance / customs contact | проверяет для «Договор поставки товаров (общий шаблон)» sanctions/export control, dangerous goods, airport security и ограничения передачи данных |

## Риски и ограничения

- Нельзя готовить договор или RAG-ответ без evidence по профилю «поставка упаковки и расходников для авиагруза»:
  purchase order, specs, certificates, batch list, delivery note, acceptance act, photos, nonconformity report.
- Ключевой риск сценария: товары не подходят для screening, temperature control, dangerous goods marking или
  airline acceptance.
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

- ГК РФ, глава 30 (поставка)
- ГК РФ, ст. 506-524 (договор поставки)

## Критерии качества ответа

- ответ решает именно сценарий «поставка упаковки и расходников для авиагруза» и не смешивает его со смежным
  договором или претензией
- источники подтверждения названы предметно: purchase order, specs, certificates, batch list, delivery note,
  acceptance act, photos, nonconformity report
- учтен профильный риск: товары не подходят для screening, temperature control, dangerous goods marking или
  airline acceptance
- если airport, flight, terminal, customs или dangerous goods не подтверждены документом, ответ запрашивает
  источник и не делает вывод по аналогии

## Контрольный список

- [ ] запрос сопоставлен с документом «Договор поставки товаров (общий шаблон)» и профилем «поставка упаковки и
  расходников для авиагруза»
- [ ] собраны профильные evidence: purchase order, specs, certificates, batch list, delivery note, acceptance
  act, photos, nonconformity report
- [ ] проверены полномочия подписанта, версия приложений, liability cap, insurance и payment terms
- [ ] оценено ограничение: товары не подходят для screening, temperature control, dangerous goods marking или
  airline acceptance
- [ ] customs/export control, dangerous goods, temperature или security условия включены только при
  подтвержденной применимости

## Порядок пересмотра и актуализации

Владелец документа: Руководитель юридического отдела. Плановый пересмотр проводится не реже одного раза в 12
месяцев.

Внеплановый пересмотр нужен после события: defective packaging, wrong labels, shortage before cutoff или
rejected shipment; также после изменения carrier/GHA rules, airport security требований, customs/export control
режима, страхового покрытия или судебной практики.

При пересмотре Legal выборочно сверяет 3-5 завершенных кейсов профиля «поставка упаковки и расходников для
авиагруза» и обновляет evidence list, сроки согласования, роли эскалации и ограничения RAG-ответа.

## История изменений

| Версия | Дата | Изменение | Автор |
|--------|------|-----------|-------|
| 1.0 | 2026-05-15 | Первичная редакция внутреннего документа | Владелец процесса |

> Применять «Договор поставки товаров (общий шаблон)» после подтверждения владельцем процесса; спорные и нетиповые кейсы требуют ручной проверки.
