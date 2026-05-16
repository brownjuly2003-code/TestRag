---
doc_id: legal_contract_services_marketing
title: Договор на маркетинговые услуги
category: Legal contract templates
document_type: договор оказания услуг
department: Legal
synthetic_demo: false
source_type: internal_controlled
version: "1.0"
effective_date: '2026-05-15'
owner_role: Руководитель юридического отдела
related_normative_sources:
- ГК РФ, глава 39 (оказание услуг)
- ФЗ от 13.03.2006 № 38-ФЗ (о рекламе)
keywords:
- маркетинг
- реклама
- агентство
confidentiality: internal
---

# Договор на маркетинговые услуги

## Назначение

Договор на маркетинговые услуги используется для сценария: подрядчик продвигает cargo capacity, route launch,
special cargo сервисы или терминальные услуги. Это рабочий шаблон Legal для авиагрузовой сделки, где предмет
проверяется по источникам, а не по названию документа.

До выпуска проекта юрист сверяет полномочия, приложения, лимиты ответственности, страхование и доказательства:
campaign brief, approved claims, rate disclaimer, route schedule, brand materials, lead report, compliance
approval. AWB/MAWB/HAWB, airport, flight, terminal, customs и dangerous goods указываются только как условия или
ограничения.

## Область применения

Документ применяется, когда запрос связан с профилем «маркетинг air cargo маршрутов» и есть операционная связка
с air cargo route, terminal handover или расчетами по перевозке.

Наземная передача упоминается только как проверяемое evidence: pickup/delivery proof, terminal slot, пломбы или
temperature log, если они действительно входят в сделку. Customs/export control, dangerous goods, temperature
cargo и security screening включаются только при подтвержденной применимости.

## Термины

- **Маркетинг air cargo маршрутов** — профиль документа, который определяет обязательные приложения и evidence.
- **Aviation evidence по сделке** — campaign brief, approved claims, rate disclaimer, route schedule, brand
  materials, lead report, compliance approval; комплект подтверждает предмет, цену, сроки, приемку и пределы
  ответственности.
- **Операционное ограничение** — маркетинг обещает тариф, срок доставки, customs clearance или dangerous goods
  acceptance без подтверждения; условие выносится в приложение, SLA или протокол разногласий.
- **Эскалационное событие** — misleading route promise, brand misuse, санкционный lead или complaint from
  carrier; после него проект возвращается к Legal, operations и finance/insurance.

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
| `agency_name` | Наименование агентства | `{{agency_name}}` |
| `campaign_description` | Описание кампании | `{{campaign_description}}` |
| `budget` | Бюджета | `{{budget}}` |
| `kpi_metrics` | KPI-метрики | `{{kpi_metrics}}` |
| `payment_schedule` | График оплаты | `{{payment_schedule}}` |
| `air_cargo_scope` | Air cargo marketing scope | `{{air_cargo_scope}}` |
| `route_campaign` | Route/capacity campaign | `{{route_campaign}}` |
| `cargo_data_access` | Доступ к cargo marketing data | `{{cargo_data_access}}` |
| `compliance_review_date` | Дата compliance review | `{{compliance_review_date}}` |

### 3. Подготовка текста

Ответственный юрист сверяет каждое поле с первичными источниками: заявку инициатора, карточку контрагента,
полномочия подписанта, коммерческое предложение, тарифы, SLA и приложения к авиагрузовой операции. Незаполненные
значения остаются плейсхолдерами `{{...}}`; AWB, booking, рейс, аэропорты, цена, штрафы, лимиты ответственности
и сроки приемки не подставляются по образцу другого договора.

### 4. Текст шаблона

```
ДОГОВОР НА МАРКЕТИНГОВЫЕ УСЛУГИ

г. {{city}}                                      {{contract_date}}

1. Стороны и полномочия
1.1. Сторона 1: {{party_1_name}}, представитель: {{party_1_representative}}.
1.2. Сторона 2: {{party_2_name}}, представитель: {{party_2_representative}}.
1.3. Полномочия подписантов подтверждаются уставом, доверенностью, решением органа управления или доверенностью
     на работу с авиагрузовыми документами.

2. Предмет и авиационные параметры
2.1. Предмет: маркетинг авиагрузовых услуг, грузовой емкости, маршрутов, terminal services, cold chain и клиентских программ.
2.2. Существенные параметры сделки:
- Номер договора: {{contract_number}}
- Дата договора: {{contract_date}}
- Наименование агентства: {{agency_name}}
- Описание кампании: {{campaign_description}}
- Бюджета: {{budget}}
- KPI-метрики: {{kpi_metrics}}
- График оплаты: {{payment_schedule}}
- Air cargo marketing scope: {{air_cargo_scope}}
- Route/capacity campaign: {{route_campaign}}
- Доступ к cargo marketing data: {{cargo_data_access}}
- Дата compliance review: {{compliance_review_date}}
2.3. В заявке или приложении указываются AWB/MAWB/HAWB или booking, flight number, airport of
     departure/destination, cutoff time, chargeable weight, terminal handling, ULD/pallet, customs/export
     control и special cargo requirements, если они применимы к операции.
2.4. Передача груза в аэропорт или из него описывается только при наличии pickup/delivery proof,
     terminal slot, пломб, temperature log или иного handover evidence, связанного с
     AWB/booking.

3. Цена, сроки, SLA и приемка
3.1. Цена, валюта, freight/handling/storage charges, порядок оплаты и chargeable weight указываются по
     согласованным тарифам, rate sheet или коммерческому предложению.
3.2. Исполнение подтверждается: бриф, route/capacity plan, rate sheets, согласованные claims, список cargo data, акты услуг и compliance approval.
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

- Владелец процесса проверяет профиль «маркетинг air cargo маршрутов», стороны, authority matrix, коммерческие
  условия и evidence: campaign brief, approved claims, rate disclaimer, route schedule, brand materials, lead
  report, compliance approval.
- Срок первичной юридической проверки — 2 рабочих дня после получения полного комплекта; для dangerous goods,
  санкций, insurance gap или airport security срок фиксируется отдельно.
- Эскалация обязательна при событии: misleading route promise, brand misuse, санкционный lead или complaint from
  carrier. Решение фиксируется в версии договора, приложении, протоколе разногласий или change log.
- Нельзя переносить AWB, flight number, airport pair, terminal status, customs status, chargeable weight или
  сумму из похожей сделки без первичного источника.

## Практический сценарий

- Сценарий: подрядчик продвигает cold chain air freight route и согласует тарифные утверждения с operations и compliance.
- Проверить: маршрут, capacity, tariff claims, cargo data, SLA statements, approvals и ограничения по рекламе.
- Подтвердить источниками: бриф, route/capacity plan, rate sheets, согласованные claims, список cargo data, акты услуг и compliance approval.
- Результат: проект содержит aviation-specific предмет, route/airport details, приемочные доказательства,
  liability cap, страхование, порядок претензий и ручную проверку special cargo/customs рисков.
- Предметная проверка: признаки «маркетинг, реклама, агентство» используются только вместе с подтвержденными AWB/booking, приложениями и операционными документами.

## Правила ответа RAG-ассистента

- Использовать документ как источник типа «договор оказания услуг» по теме «Договор на маркетинговые услуги» только при совпадении запроса с авиагрузовым предметом документа.
- Перед ответом проверить: маршрут, capacity, tariff claims, cargo data, SLA statements, approvals и ограничения по рекламе; полномочия подписантов, маршрут согласования, версию приложений и aviation evidence.
- Если нет AWB/booking, flight number, airport pair, cargo terminal status, цены, срока, акта приемки или
  ключевого факта, сначала вернуть уточняющие вопросы и не подставлять данные по догадке.
- Dangerous goods, temperature, customs/export control, санкции, валюту, страхование и cargo data передавать на
  ручную проверку.

## Доказательства и источники для ответа

- Профильные источники: campaign brief, approved claims, rate disclaimer, route schedule, brand materials, lead
  report, compliance approval.
- Корпоративные источники: заявка инициатора, карточка контрагента, authority matrix, коммерческое предложение,
  приложения, страховой или финансовый approval.
- Ограничение для ответа: маркетинг обещает тариф, срок доставки, customs clearance или dangerous goods
  acceptance без подтверждения. Если источник не подтверждает его, RAG-ответ указывает пробел и не подменяет его
  общей договорной нормой.
- Airport, flight, terminal, customs и dangerous goods используются как проверяемые факты: дата, статус, акт,
  разрешение, отметка или запрет.

## Типовые пользовательские запросы

| Запрос пользователя | Безопасная реакция ассистента |
|---------------------|-------------------------------|
| Подходит ли «Договор на маркетинговые услуги» для авиагрузовой сделки? | Сопоставить предмет, стороны, AWB/booking, аэропорты, SLA, special cargo и обязательные приложения; назвать недостающие факты и риски. |
| Сделай черновик договора. | Собрать поля; не выдумывать цену, рейс, AWB, cutoff time и реквизиты. |
| Документы для air cargo? | AWB, booking, invoice, packing list, акты, SLA, страхование, customs/export control. |
| Можно ли применить автоматически? | Проверить DG, temperature, customs/export control, sanctions и liability cap. |

## Ответственные роли

| Роль | Зона ответственности |
|------|----------------------|
| Руководитель юридического отдела | утверждает позицию по профилю «маркетинг air cargo маршрутов», liability cap, waiver и нестандартные приложения |
| Cargo marketing owner | подтверждает operational facts: campaign brief, approved claims, rate disclaimer, route schedule, brand materials, lead report, compliance approval |
| Finance / insurance owner | сверяет тарифы, оплату, reserves, страховое покрытие, deductible и право регресса |
| Compliance / customs contact | проверяет для «Договор на маркетинговые услуги» sanctions/export control, dangerous goods, airport security и ограничения передачи данных |

## Риски и ограничения

- Нельзя готовить договор или RAG-ответ без evidence по профилю «маркетинг air cargo маршрутов»: campaign brief,
  approved claims, rate disclaimer, route schedule, brand materials, lead report, compliance approval.
- Ключевой риск сценария: маркетинг обещает тариф, срок доставки, customs clearance или dangerous goods
  acceptance без подтверждения.
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

- ГК РФ, глава 39 (оказание услуг)
- ФЗ от 13.03.2006 № 38-ФЗ (о рекламе)

## Критерии качества ответа

- ответ решает именно сценарий «маркетинг air cargo маршрутов» и не смешивает его со смежным договором или
  претензией
- источники подтверждения названы предметно: campaign brief, approved claims, rate disclaimer, route schedule,
  brand materials, lead report, compliance approval
- учтен профильный риск: маркетинг обещает тариф, срок доставки, customs clearance или dangerous goods
  acceptance без подтверждения
- если airport, flight, terminal, customs или dangerous goods не подтверждены документом, ответ запрашивает
  источник и не делает вывод по аналогии

## Контрольный список

- [ ] запрос сопоставлен с документом «Договор на маркетинговые услуги» и профилем «маркетинг air cargo
  маршрутов»
- [ ] собраны профильные evidence: campaign brief, approved claims, rate disclaimer, route schedule, brand
  materials, lead report, compliance approval
- [ ] проверены полномочия подписанта, версия приложений, liability cap, insurance и payment terms
- [ ] оценено ограничение: маркетинг обещает тариф, срок доставки, customs clearance или dangerous goods
  acceptance без подтверждения
- [ ] customs/export control, dangerous goods, temperature или security условия включены только при
  подтвержденной применимости

## Порядок пересмотра и актуализации

Владелец документа: Руководитель юридического отдела. Плановый пересмотр проводится не реже одного раза в 12
месяцев.

Внеплановый пересмотр нужен после события: misleading route promise, brand misuse, санкционный lead или
complaint from carrier; также после изменения carrier/GHA rules, airport security требований, customs/export
control режима, страхового покрытия или судебной практики.

При пересмотре Legal выборочно сверяет 3-5 завершенных кейсов профиля «маркетинг air cargo маршрутов» и
обновляет evidence list, сроки согласования, роли эскалации и ограничения RAG-ответа.

## История изменений

| Версия | Дата | Изменение | Автор |
|--------|------|-----------|-------|
| 1.0 | 2026-05-15 | Первичная редакция внутреннего документа | Владелец процесса |

> Применять «Договор на маркетинговые услуги» после подтверждения владельцем процесса; спорные и нетиповые кейсы требуют ручной проверки.
