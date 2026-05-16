---
doc_id: legal_contract_subcontract
title: Договор субподряда
category: Legal contract templates
document_type: договор
department: Legal
synthetic_demo: false
source_type: internal_controlled
version: "1.0"
effective_date: '2026-05-15'
owner_role: Руководитель юридического отдела
related_normative_sources:
- ГК РФ, глава 37 (подряд)
- ГК РФ, ст. 706-707 (субподряд)
keywords:
- субподряд
- генподрядчик
- выполнение работ
confidentiality: internal
---

# Договор субподряда

## Назначение

Договор субподряда используется для сценария: основной исполнитель передает часть terminal, screening, storage
или forwarding duties субподрядчику. Это рабочий шаблон Legal для авиагрузовой сделки, где предмет проверяется
по источникам, а не по названию документа.

До выпуска проекта юрист сверяет полномочия, приложения, лимиты ответственности, страхование и доказательства:
subcontract scope, main contract flow-down, AWB/booking list, terminal permits, SLA, incident reporting,
insurance. AWB/MAWB/HAWB, airport, flight, terminal, customs и dangerous goods указываются только как условия
или ограничения.

## Область применения

Документ применяется, когда запрос связан с профилем «субподряд handling/forwarding work» и есть операционная
связка с air cargo route, terminal handover или расчетами по перевозке.

Наземная передача упоминается только как проверяемое evidence: pickup/delivery proof, terminal slot, пломбы или
temperature log, если они действительно входят в сделку. Customs/export control, dangerous goods, temperature
cargo и security screening включаются только при подтвержденной применимости.

## Термины

- **Субподряд handling/forwarding work** — профиль документа, который определяет обязательные приложения и
  evidence.
- **Aviation evidence по сделке** — subcontract scope, main contract flow-down, AWB/booking list, terminal
  permits, SLA, incident reporting, insurance; комплект подтверждает предмет, цену, сроки, приемку и пределы
  ответственности.
- **Операционное ограничение** — субподрядчик не принимает flow-down по liability, security, dangerous goods или
  evidence reporting; условие выносится в приложение, SLA или протокол разногласий.
- **Эскалационное событие** — GHA incident, missed cutoff, subcontractor denial, insurance gap или customer
  claim; после него проект возвращается к Legal, operations и finance/insurance.

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
| `general_contractor_name` | Наименование генерального подрядчика | `{{general_contractor_name}}` |
| `subcontractor_name` | Наименование субподрядчика | `{{subcontractor_name}}` |
| `main_contract_ref` | Ссылка на основной договор | `{{main_contract_ref}}` |
| `work_description` | Описание работы | `{{work_description}}` |
| `price` | Цена | `{{price}}` |
| `deadline` | Срок исполнения | `{{deadline}}` |
| `quality_requirements` | Качества требований | `{{quality_requirements}}` |
| `service_order_ref` | Service order | `{{service_order_ref}}` |
| `awb_booking_ref` | AWB/booking | `{{awb_booking_ref}}` |
| `rate_sheet_ref` | Rate sheet | `{{rate_sheet_ref}}` |
| `sla_appendix` | SLA appendix | `{{sla_appendix}}` |
| `airport_scope` | Airport/terminal scope | `{{airport_scope}}` |

### 3. Подготовка текста

Ответственный юрист сверяет каждое поле с первичными источниками: заявку инициатора, карточку контрагента,
полномочия подписанта, коммерческое предложение, тарифы, SLA и приложения к авиагрузовой операции. Незаполненные
значения остаются плейсхолдерами `{{...}}`; AWB, booking, рейс, аэропорты, цена, штрафы, лимиты ответственности
и сроки приемки не подставляются по образцу другого договора.

### 4. Текст шаблона

```
ДОГОВОР СУБПОДРЯДА

г. {{city}}                                      {{contract_date}}

1. Стороны и полномочия
1.1. Сторона 1: {{party_1_name}}, представитель: {{party_1_representative}}.
1.2. Сторона 2: {{party_2_name}}, представитель: {{party_2_representative}}.
1.3. Полномочия подписантов подтверждаются уставом, доверенностью, решением органа управления или доверенностью
     на работу с авиагрузовыми документами.

2. Предмет и авиационные параметры
2.1. Предмет: рамочное регулирование авиагрузовых заявок, тарифов, SLA, терминальной обработки, экспедирования,
     таможни и поставок.
2.2. Существенные параметры сделки:
- Номер договора: {{contract_number}}
- Дата договора: {{contract_date}}
- Наименование генерального подрядчика: {{general_contractor_name}}
- Наименование субподрядчика: {{subcontractor_name}}
- Ссылка на основной договор: {{main_contract_ref}}
- Описание работы: {{work_description}}
- Цена: {{price}}
- Срок исполнения: {{deadline}}
- Качества требований: {{quality_requirements}}
- Service order: {{service_order_ref}}
- AWB/booking: {{awb_booking_ref}}
- Rate sheet: {{rate_sheet_ref}}
- SLA appendix: {{sla_appendix}}
- Airport/terminal scope: {{airport_scope}}
2.3. В заявке или приложении указываются AWB/MAWB/HAWB или booking, flight number, airport of
     departure/destination, cutoff time, chargeable weight, terminal handling, ULD/pallet, customs/export
     control и special cargo requirements, если они применимы к операции.
2.4. Передача груза в аэропорт или из него описывается только при наличии pickup/delivery proof,
     terminal slot, пломб, temperature log или иного handover evidence, связанного с
     AWB/booking.

3. Цена, сроки, SLA и приемка
3.1. Цена, валюта, freight/handling/storage charges, порядок оплаты и chargeable weight указываются по
     согласованным тарифам, rate sheet или коммерческому предложению.
3.2. Исполнение подтверждается: service order, AWB/booking, rate sheet, SLA appendix, акты terminal handling,
     отчеты forwarder и протоколы разногласий.
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

- Владелец процесса проверяет профиль «субподряд handling/forwarding work», стороны, authority matrix,
  коммерческие условия и evidence: subcontract scope, main contract flow-down, AWB/booking list, terminal
  permits, SLA, incident reporting, insurance.
- Срок первичной юридической проверки — 2 рабочих дня после получения полного комплекта; для dangerous goods,
  санкций, insurance gap или airport security срок фиксируется отдельно.
- Эскалация обязательна при событии: GHA incident, missed cutoff, subcontractor denial, insurance gap или
  customer claim. Решение фиксируется в версии договора, приложении, протоколе разногласий или change log.
- Нельзя переносить AWB, flight number, airport pair, terminal status, customs status, chargeable weight или
  сумму из похожей сделки без первичного источника.

## Практический сценарий

- Сценарий: стороны заключают master agreement для регулярных авиагрузовых отправок и оформляют каждую партию
  service order.
- Проверить: заявки, тарифы, аэропорты, SLA, terminal handling, special cargo, ответственность и претензии.
- Подтвердить источниками: service order, AWB/booking, rate sheet, SLA appendix, акты terminal handling, отчеты
  forwarder и протоколы разногласий.
- Результат: проект содержит aviation-specific предмет, route/airport details, приемочные доказательства,
  liability cap, страхование, порядок претензий и ручную проверку special cargo/customs рисков.
- Предметная проверка: признаки «субподряд, генподрядчик, выполнение работ» используются только вместе с подтвержденными AWB/booking, приложениями и операционными документами.

## Правила ответа RAG-ассистента

- Использовать документ как источник типа «договор» по теме «Договор субподряда» только при совпадении запроса с авиагрузовым предметом документа.
- Перед ответом проверить: заявки, тарифы, аэропорты, SLA, terminal handling, special cargo, ответственность и
  претензии; полномочия подписантов, маршрут согласования, версию приложений и aviation evidence.
- Если нет AWB/booking, flight number, airport pair, cargo terminal status, цены, срока, акта приемки или
  ключевого факта, сначала вернуть уточняющие вопросы и не подставлять данные по догадке.
- Dangerous goods, temperature, customs/export control, санкции, валюту, страхование и cargo data передавать на
  ручную проверку.

## Доказательства и источники для ответа

- Профильные источники: subcontract scope, main contract flow-down, AWB/booking list, terminal permits, SLA,
  incident reporting, insurance.
- Корпоративные источники: заявка инициатора, карточка контрагента, authority matrix, коммерческое предложение,
  приложения, страховой или финансовый approval.
- Ограничение для ответа: субподрядчик не принимает flow-down по liability, security, dangerous goods или
  evidence reporting. Если источник не подтверждает его, RAG-ответ указывает пробел и не подменяет его общей
  договорной нормой.
- Airport, flight, terminal, customs и dangerous goods используются как проверяемые факты: дата, статус, акт,
  разрешение, отметка или запрет.

## Типовые пользовательские запросы

| Запрос пользователя | Безопасная реакция ассистента |
|---------------------|-------------------------------|
| Подходит ли «Договор субподряда» для авиагрузовой сделки? | Сопоставить предмет, стороны, AWB/booking, аэропорты, SLA, special cargo и обязательные приложения; назвать недостающие факты и риски. |
| Сделай черновик договора. | Собрать поля; не выдумывать цену, рейс, AWB, cutoff time и реквизиты. |
| Документы для air cargo? | AWB, booking, invoice, packing list, акты, SLA, страхование, customs/export control. |
| Можно ли применить автоматически? | Проверить DG, temperature, customs/export control, sanctions и liability cap. |

## Ответственные роли

| Роль | Зона ответственности |
|------|----------------------|
| Руководитель юридического отдела | утверждает позицию по профилю «субподряд handling/forwarding work», liability cap, waiver и нестандартные приложения |
| Subcontract owner | подтверждает operational facts: subcontract scope, main contract flow-down, AWB/booking list, terminal permits, SLA, incident reporting, insurance |
| Finance / insurance owner | сверяет тарифы, оплату, reserves, страховое покрытие, deductible и право регресса |
| Compliance / customs contact | проверяет для «Договор субподряда» sanctions/export control, dangerous goods, airport security и ограничения передачи данных |

## Риски и ограничения

- Нельзя готовить договор или RAG-ответ без evidence по профилю «субподряд handling/forwarding work»:
  subcontract scope, main contract flow-down, AWB/booking list, terminal permits, SLA, incident reporting,
  insurance.
- Ключевой риск сценария: субподрядчик не принимает flow-down по liability, security, dangerous goods или
  evidence reporting.
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

- ГК РФ, глава 37 (подряд)
- ГК РФ, ст. 706-707 (субподряд)

## Критерии качества ответа

- ответ решает именно сценарий «субподряд handling/forwarding work» и не смешивает его со смежным договором или
  претензией
- источники подтверждения названы предметно: subcontract scope, main contract flow-down, AWB/booking list,
  terminal permits, SLA, incident reporting, insurance
- учтен профильный риск: субподрядчик не принимает flow-down по liability, security, dangerous goods или
  evidence reporting
- если airport, flight, terminal, customs или dangerous goods не подтверждены документом, ответ запрашивает
  источник и не делает вывод по аналогии

## Контрольный список

- [ ] запрос сопоставлен с документом «Договор субподряда» и профилем «субподряд handling/forwarding work»
- [ ] собраны профильные evidence: subcontract scope, main contract flow-down, AWB/booking list, terminal
  permits, SLA, incident reporting, insurance
- [ ] проверены полномочия подписанта, версия приложений, liability cap, insurance и payment terms
- [ ] оценено ограничение: субподрядчик не принимает flow-down по liability, security, dangerous goods или
  evidence reporting
- [ ] customs/export control, dangerous goods, temperature или security условия включены только при
  подтвержденной применимости

## Порядок пересмотра и актуализации

Владелец документа: Руководитель юридического отдела. Плановый пересмотр проводится не реже одного раза в 12
месяцев.

Внеплановый пересмотр нужен после события: GHA incident, missed cutoff, subcontractor denial, insurance gap или
customer claim; также после изменения carrier/GHA rules, airport security требований, customs/export control
режима, страхового покрытия или судебной практики.

При пересмотре Legal выборочно сверяет 3-5 завершенных кейсов профиля «субподряд handling/forwarding work» и
обновляет evidence list, сроки согласования, роли эскалации и ограничения RAG-ответа.

## История изменений

| Версия | Дата | Изменение | Автор |
|--------|------|-----------|-------|
| 1.0 | 2026-05-15 | Первичная редакция внутреннего документа | Владелец процесса |

> Применять «Договор субподряда» после подтверждения владельцем процесса; спорные и нетиповые кейсы требуют ручной проверки.
