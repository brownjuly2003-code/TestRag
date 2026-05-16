---
doc_id: legal_claim_ip_infringement
title: Претензия по неправомерной маркировке и cargo data в авиаперевозке
category: Claims, disputes and legal letters
document_type: претензия контрагенту
department: Legal
synthetic_demo: false
source_type: internal_controlled
version: "1.0"
effective_date: '2026-05-15'
owner_role: Руководитель юридического отдела
related_normative_sources:
- ГК РФ, часть 4 (интеллектуальные права)
- Воздушный кодекс РФ
- ТК ЕАЭС
keywords:
- air cargo
- AWB
- претензия
- терминал
- спор
confidentiality: internal
---

# Претензия по неправомерной маркировке и cargo data в авиаперевозке

## Назначение

Претензия по неправомерной маркировке и cargo data в авиаперевозке используется для сценария: контрагент
использует бренд, labels, route data или customer data вне разрешенного air cargo сценария. Это претензия
контрагенту для конкретного air cargo dispute, а не общая форма без shipment evidence.

Позиция строится на доказательствах: approved label mockups, AWB data extract, photos of cargo labels, brand
permission, access log, correspondence, takedown notice. AWB/MAWB/HAWB, airport pair, flight number,
terminal/GHA records, customs и dangerous goods учитываются только как проверяемые факты, ограничения или
причины эскалации.

## Область применения

Документ применяется, когда карточка спора подтверждает профиль «неправомерная маркировка и cargo data», сторону
спора, сумму или требование, срок ответа и способ вручения.

Если не хватает AWB/booking, terminal act, customs record или proof of delivery, готовится запрос evidence без
признания вины или долга. Для события «urgent stop-use notice, data access freeze или brand compliance review»
Legal согласует escalation route с operations, finance, insurer, broker или external counsel.

## Термины

- **Неправомерная маркировка и cargo data** — профиль претензии или письма, который определяет предмет
  доказывания и безопасную позицию.
- **Evidence bundle** — approved label mockups, AWB data extract, photos of cargo labels, brand permission,
  access log, correspondence, takedown notice; комплект используется для chronology, liability, amount,
  mitigation и вручения.
- **Без признания** — ответ не подтверждает долг, вину, causation, размер ущерба, waiver of rights или отказ от
  liability cap.
- **Escalation trigger** — urgent stop-use notice, data access freeze или brand compliance review; событие
  требует решения по сроку ответа, settlement authority и уведомлению страховщика или руководителя.

## Порядок действий

### 1. Инициирование

Инициатор передает юристу карточку спора: описание события, AWB/MAWB/HAWB, booking, flight number, airport pair,
cargo manifest, доказательства вручения, расчет требования и переписку с авиаперевозчиком, GHA, экспедитором,
customs broker или страховщиком. До подготовки текста юрист проверяет claim notice deadline, договорный срок
ответа, limitation period, полномочия подписанта и маршрут эскалации.

### 2. Обязательные поля

| Поле | Назначение | Пример заполнения |
|------|------------|-------------------|
| `dispute_card_id` | Номер карточки спора | `{{dispute_card_id}}` |
| `awb_mawb_hawb` | AWB/MAWB/HAWB | `{{awb_mawb_hawb}}` |
| `booking_number` | Booking / номер бронирования | `{{booking_number}}` |
| `flight_number` | Flight number | `{{flight_number}}` |
| `airport_pair` | Аэропорт отправления и назначения | `{{airport_pair}}` |
| `cargo_manifest_ref` | Cargo manifest / manifest extract | `{{cargo_manifest_ref}}` |
| `terminal_act_ref` | Акт терминала или GHA | `{{terminal_act_ref}}` |
| `event_datetime` | Дата и время события в local airport time | `{{event_datetime}}` |
| `claim_amount` | Сумма требования, резерва или спорного начисления | `{{claim_amount}}` |
| `response_deadline` | Срок ответа и следующее действие | `{{response_deadline}}` |

### 3. Подготовка текста

Каждое поле сверяется с AWB/booking, cargo manifest, terminal/GHA records, customs/handling/screening отметками,
temperature log при special cargo, платежными документами и перепиской. Плейсхолдеры `{{...}}` сохраняются для
неподтвержденных значений; нельзя заимствовать рейс, вес, сумму, срок, customs status, причину offload или
размер ущерба из похожего спора.

### 4. Текст шаблона

```
Исх. № {{letter_number}} от {{letter_date}}
Кому: {{counterparty_name}}
Способ вручения: {{delivery_method}}

Претензия по неправомерной маркировке и cargo data в авиаперевозке

1. Основание обращения
Договор / SLA / заявка / AWB terms: {{contract_ref}}.
Карточка спора: {{dispute_card_id}}.

2. Фактические обстоятельства
- AWB/MAWB/HAWB: {{awb_mawb_hawb}}
- Booking / flight number: {{booking_number}} / {{flight_number}}
- Airport pair: {{airport_pair}}
- Cargo manifest: {{cargo_manifest_ref}}
- Акт терминала/GHA: {{terminal_act_ref}}
- Событие: {{event_datetime}}, {{breach_description}}
- Сумма требования или спорного начисления: {{claim_amount}}

3. Доказательства
Приложения: AWB/MAWB/HAWB, booking, flight status, cargo manifest, акт терминала/GHA, фото,
customs/handling/screening отметки, temperature log при special cargo, invoices и переписка с
carrier/GHA/forwarder/insurer.

4. Требование или позиция
Просим {{requested_action}} в срок до {{response_deadline}}.
Настоящее письмо не является признанием долга, вины, размера ущерба, отказом от прав или отказом от лимитов
ответственности перевозчика, GHA, экспедитора либо страховщика.

Подписант __________________ / {{signatory_name}} /
```

### 5. Согласование

Документ согласуют юрист по спору, air cargo operations, финансы и владелец процесса. Compliance, customs
broker, GHA/terminal, carrier manager или страховщик подключаются при dangerous goods, temperature-controlled
cargo, customs/export control, санкциях, cargo data, валютных платежах, страховом случае или нестандартном
liability cap. Любая правка суммы, срока, признания фактов, waiver, settlement или полномочий возвращает
документ на повторное согласование.

### 6. Подписание, вручение и хранение

Финальная версия, приложения, proof of delivery, evidence bundle, calculation file, insurance notice, ответы
контрагентов и процессуальный календарь хранятся в карточке спора. Способ вручения фиксируется отдельно: ЭДО,
договорный email, courier delivery, почта с описью, portal carrier/GHA или иной канал, предусмотренный
договором, AWB terms или перепиской.

## Рабочие доказательства, сроки и эскалация

- Владелец спора сверяет профиль «неправомерная маркировка и cargo data», карточку спора, срок ответа, способ
  вручения и evidence: approved label mockups, AWB data extract, photos of cargo labels, brand permission,
  access log, correspondence, takedown notice.
- Первичный legal triage выполняется в течение 1 рабочего дня; проект претензии, ответа или письма готовится в
  срок из договора, claim notice или процессуального календаря.
- Эскалация обязательна при событии: urgent stop-use notice, data access freeze или brand compliance review. До
  решения текст не должен признавать долг, вину, causation, сумму ущерба или отказ от прав.
- Если customs, dangerous goods, airport security, temperature или terminal release являются причиной спора, они
  подтверждаются актом, отметкой, запросом органа, логом или письмом.

## Практический сценарий

- Сценарий: на cargo labels и HAWB использована чужая маркировка, что вызвало customs hold.
- Проверить: AWB/MAWB/HAWB, booking, flight number, airport pair, cargo manifest, terminal/GHA act,
  customs/handling/screening отметки, temperature log, invoices, proof of delivery и claim deadline.
- Подтвердить источниками: AWB/MAWB/HAWB, booking, flight number, cargo manifest, акт терминала или GHA, фото повреждения или расхождения, отметки screening/handling/customs, temperature log при special cargo, invoices/rate sheet, переписка с авиаперевозчиком, GHA, экспедитором, customs broker и страховщиком. Дополнительно: trademark certificate, фото cargo labels, HAWB/manifest extract, customs notice.
- Результат: юрист формирует позицию без признания вины, долга, размера ущерба или отказа от прав; отдельно
  фиксируются срок ответа, способ вручения, следующий deadline и проверка лимитов ответственности
  carrier/GHA/forwarder/insurer.
- Предметная проверка: признаки air cargo, AWB, терминал, рейс, handling, customs и temperature используются
  только вместе с подтвержденной карточкой спора.

## Правила ответа RAG-ассистента

- Использовать документ как источник типа «претензия контрагенту» по теме «Претензия по неправомерной маркировке и cargo data в авиаперевозке» только при фактическом совпадении запроса с air cargo dispute.
- Перед ответом проверить AWB/MAWB/HAWB, booking, flight number, airport pair, cargo manifest, terminal/GHA акт,
  customs/handling/screening records, temperature log при special cargo, доказательства вручения и срок ответа.
- Если ключевых фактов нет, сначала вернуть уточняющие вопросы и не подставлять даты, суммы, airport codes,
  weight, flight number, AWB, customs status или реквизиты по догадке.
- Для спорных сумм, санкций, customs/export control, dangerous goods, insurance, персональных данных и cargo
  data явно указывать необходимость ручной проверки владельцем процесса.
- Не признавать долг, вину, размер ущерба, причинную связь, отказ от возражений или waiver of rights без прямого
  письменного согласования юриста.

## Доказательства и источники для ответа

- Основные источники: approved label mockups, AWB data extract, photos of cargo labels, brand permission, access
  log, correspondence, takedown notice.
- Дополнительные источники: договор или заказ, SLA/rate sheet, расчет требования, доказательство вручения,
  переписка с carrier, GHA, forwarder, customs broker, insurer и клиентом.
- Проверяемое ограничение: нельзя смешивать IP claim с cargo damage claim без доказательства использования
  маркировки или данных.
- Airport, flight, terminal, customs и dangerous goods не используются как общий ярлык; указывается source,
  дата, статус, responsible party и влияние на deadline, liability или amount.

## Типовые пользовательские запросы

| Запрос пользователя | Безопасная реакция ассистента |
|---------------------|-------------------------------|
| Подготовь претензию или ответ. | Запросить AWB/booking, flight, cargo manifest, terminal records и срок ответа. |
| Какие доказательства приложить? | AWB, booking, cargo manifest, акт терминала/GHA, фото, отметки и переписку. |
| Можно ли признать требования или settlement? | Только после ручного согласования юриста, финансов и страховщика. |
| Какие факты нужны для «Претензия по неправомерной маркировке и cargo data в авиаперевозке»? | Перечислить недостающие AWB, booking, рейс, airport pair, timeline события, сумму, доказательства вручения и ответственных. |

## Ответственные роли

| Роль | Зона ответственности |
|------|----------------------|
| Руководитель юридического отдела | утверждает позицию по профилю «неправомерная маркировка и cargo data», settlement authority, waiver и спорные liability caps |
| Brand compliance lead | ведет chronology, evidence bundle, срок ответа и коммуникацию по событию: urgent stop-use notice, data access freeze или brand compliance review |
| Air cargo operations / GHA contact | подтверждает для «Претензия по неправомерной маркировке и cargo data в авиаперевозке» movement, acceptance/offload/release, terminal act, handling records и operational root cause |
| Finance / insurer / broker contact | сверяет по «Претензия по неправомерной маркировке и cargo data в авиаперевозке» сумму требования, reserve, оплату, customs costs, insurance notice и право регресса |

## Риски и ограничения

- Нельзя направлять документ без evidence по профилю «неправомерная маркировка и cargo data»: approved label
  mockups, AWB data extract, photos of cargo labels, brand permission, access log, correspondence, takedown
  notice.
- Ключевое ограничение: нельзя смешивать IP claim с cargo damage claim без доказательства использования
  маркировки или данных.
- AWB/MAWB/HAWB, flight status, cargo manifest и terminal records подтверждают timeline, но не заменяют анализ
  договора, liability cap, notice deadline и causation.
- Формулировки сохраняют safe position: without prejudice / без признания долга, вины, размера ущерба, причинной
  связи и без отказа от прав.

## Связанные документы

- `MANIFEST.md`
- `NORMATIVE_SOURCE_MANIFEST.md`
- `04_legal_letter_demand.md`
- `04_legal_memo_dispute_risk.md`
- `04_legal_reply_non_payment.md`
- `03_legal_contract_customs_broker.md`
- `05_tlog_contract_transport_air.md`

## Нормативные ориентиры

- ГК РФ, часть 4 (интеллектуальные права)
- Воздушный кодекс РФ
- ТК ЕАЭС

## Критерии качества ответа

- ответ относится к профилю «неправомерная маркировка и cargo data» и не подменяет его общей претензионной
  процедурой
- доказательства названы предметно: approved label mockups, AWB data extract, photos of cargo labels, brand
  permission, access log, correspondence, takedown notice
- отдельно указано ограничение или gap: нельзя смешивать IP claim с cargo damage claim без доказательства
  использования маркировки или данных
- срок ответа, способ вручения, escalation route и safe legal position отражены явно

## Контрольный список

- [ ] карточка спора сопоставлена с документом «Претензия по неправомерной маркировке и cargo data в
  авиаперевозке» и профилем «неправомерная маркировка и cargo data»
- [ ] собран evidence bundle: approved label mockups, AWB data extract, photos of cargo labels, brand
  permission, access log, correspondence, takedown notice
- [ ] проверены claim notice, limitation period, proof of delivery/service и authority signer
- [ ] оценено ограничение: нельзя смешивать IP claim с cargo damage claim без доказательства использования
  маркировки или данных
- [ ] текст не признает долг, вину, causation, размер ущерба или waiver без отдельного approval

## Порядок пересмотра и актуализации

Владелец документа: Руководитель юридического отдела. Плановый пересмотр проводится не реже одного раза в 12
месяцев.

Внеплановый пересмотр нужен после события: urgent stop-use notice, data access freeze или brand compliance
review; также после нового claim pattern, изменения carrier/GHA rules, customs practice, insurance wording,
limitation period или судебной практики.

При пересмотре Legal проверяет закрытые дела профиля «неправомерная маркировка и cargo data»: какие evidence
сработали, какие сроки были сорваны, где RAG-ответ требовал safe-position предупреждения.

## История изменений

| Версия | Дата | Изменение | Автор |
|--------|------|-----------|-------|
| 1.0 | 2026-05-15 | Первичная редакция внутреннего документа | Владелец процесса |

> Применять «Претензия по неправомерной маркировке и cargo data в авиаперевозке» после подтверждения владельцем процесса; спорные и нетиповые кейсы требуют ручной проверки.
