---
doc_id: legal_power_of_attorney_court
title: Доверенность на представительство в суде по air cargo dispute
category: Claims, disputes and legal letters
document_type: доверенность
department: Legal
synthetic_demo: false
source_type: internal_controlled
version: "1.0"
effective_date: '2026-05-15'
owner_role: Руководитель юридического отдела
related_normative_sources:
- ГК РФ, ст. 185-189 (доверенность)
- Воздушный кодекс РФ
- АПК РФ
keywords:
- air cargo
- AWB
- претензия
- терминал
- спор
confidentiality: internal
---

# Доверенность на представительство в суде по air cargo dispute

## Назначение

Доверенность на представительство в суде по air cargo dispute используется для сценария: представитель ведет
судебный спор по damage, delay, debt или service failure. Это доверенность для конкретного air cargo dispute, а
не общую форму без shipment evidence.

Позиция строится на доказательствах: court file, claim draft, evidence bundle, AWB/HAWB, calculation, proof of
service, authority approvals. AWB/MAWB/HAWB, airport pair, flight number, terminal/GHA records, customs и
dangerous goods учитываются только как проверяемые факты, ограничения или причины эскалации.

## Область применения

Документ применяется, когда карточка спора подтверждает профиль «представительство в суде», сторону спора, сумму
или требование, срок ответа и способ вручения.

Если не хватает AWB/booking, terminal act, customs record или proof of delivery, готовится запрос evidence без
признания вины или долга. Для события «hearing date, filing deadline или enforcement action» Legal согласует
escalation route с operations, finance, insurer, broker или external counsel.

## Термины

- **Представительство в суде** — профиль претензии или письма, который определяет предмет доказывания и
  безопасную позицию.
- **Evidence bundle** — court file, claim draft, evidence bundle, AWB/HAWB, calculation, proof of service,
  authority approvals; комплект используется для chronology, liability, amount, mitigation и вручения.
- **Без признания** — ответ не подтверждает долг, вину, causation, размер ущерба, waiver of rights или отказ от
  liability cap.
- **Escalation trigger** — hearing date, filing deadline или enforcement action; событие требует решения по
  сроку ответа, settlement authority и уведомлению страховщика или руководителя.

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
ДОВЕРЕННОСТЬ / ПРОЕКТ ПОЛНОМОЧИЙ

Доверитель: {{principal_name}}
Представитель: {{attorney_name}}
Предмет полномочий: Доверенность на представительство в суде по air cargo dispute

1. Air cargo scope
- AWB/MAWB/HAWB: {{awb_mawb_hawb}}
- Booking / flight number: {{booking_number}} / {{flight_number}}
- Airport pair и cargo terminal/GHA: {{airport_pair}} / {{terminal_or_gha}}
- Карточка спора: {{dispute_card_id}}

2. Разрешенные действия
Представитель вправе получать и подавать документы по AWB/booking, запрашивать terminal/GHA/carrier/customs
records, подписывать процессуальные и претензионные документы в пределах {{authority_scope}}, взаимодействовать
со страховщиком и получать копии evidence bundle.

3. Ограничения
Представитель не вправе признавать долг, вину, размер ущерба, отказываться от требований или возражений,
подписывать settlement, получать деньги либо менять liability cap без отдельного письменного решения доверителя.

Срок действия: {{validity_period}}
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

- Владелец спора сверяет профиль «представительство в суде», карточку спора, срок ответа, способ вручения и
  evidence: court file, claim draft, evidence bundle, AWB/HAWB, calculation, proof of service, authority
  approvals.
- Первичный legal triage выполняется в течение 1 рабочего дня; проект претензии, ответа или письма готовится в
  срок из договора, claim notice или процессуального календаря.
- Эскалация обязательна при событии: hearing date, filing deadline или enforcement action. До решения текст не
  должен признавать долг, вину, causation, сумму ущерба или отказ от прав.
- Если customs, dangerous goods, airport security, temperature или terminal release являются причиной спора, они
  подтверждаются актом, отметкой, запросом органа, логом или письмом.

## Практический сценарий

- Сценарий: юрист представляет компанию в суде по terminal damage claim.
- Проверить: AWB/MAWB/HAWB, booking, flight number, airport pair, cargo manifest, terminal/GHA act,
  customs/handling/screening отметки, temperature log, invoices, proof of delivery и claim deadline.
- Подтвердить источниками: AWB/MAWB/HAWB, booking, flight number, cargo manifest, акт терминала или GHA, фото повреждения или расхождения, отметки screening/handling/customs, temperature log при special cargo, invoices/rate sheet, переписка с авиаперевозчиком, GHA, экспедитором, customs broker и страховщиком. Дополнительно: case number, court, pretrial claim, evidence bundle, special court powers.
- Результат: юрист формирует позицию без признания вины, долга, размера ущерба или отказа от прав; отдельно
  фиксируются срок ответа, способ вручения, следующий deadline и проверка лимитов ответственности
  carrier/GHA/forwarder/insurer.
- Предметная проверка: признаки air cargo, AWB, терминал, рейс, handling, customs и temperature используются
  только вместе с подтвержденной карточкой спора.

## Правила ответа RAG-ассистента

- Использовать документ как источник типа «доверенность» по теме «Доверенность на представительство в суде по air cargo dispute» только при фактическом совпадении запроса с air cargo dispute.
- Перед ответом проверить AWB/MAWB/HAWB, booking, flight number, airport pair, cargo manifest, terminal/GHA акт,
  customs/handling/screening records, temperature log при special cargo, доказательства вручения и срок ответа.
- Если ключевых фактов нет, сначала вернуть уточняющие вопросы и не подставлять даты, суммы, airport codes,
  weight, flight number, AWB, customs status или реквизиты по догадке.
- Для спорных сумм, санкций, customs/export control, dangerous goods, insurance, персональных данных и cargo
  data явно указывать необходимость ручной проверки владельцем процесса.
- Не признавать долг, вину, размер ущерба, причинную связь, отказ от возражений или waiver of rights без прямого
  письменного согласования юриста.

## Доказательства и источники для ответа

- Основные источники: court file, claim draft, evidence bundle, AWB/HAWB, calculation, proof of service,
  authority approvals.
- Дополнительные источники: договор или заказ, SLA/rate sheet, расчет требования, доказательство вручения,
  переписка с carrier, GHA, forwarder, customs broker, insurer и клиентом.
- Проверяемое ограничение: нельзя включать право признания иска, отказа или мирового соглашения без explicit
  approval.
- Airport, flight, terminal, customs и dangerous goods не используются как общий ярлык; указывается source,
  дата, статус, responsible party и влияние на deadline, liability или amount.

## Типовые пользовательские запросы

| Запрос пользователя | Безопасная реакция ассистента |
|---------------------|-------------------------------|
| Подготовь претензию или ответ. | Запросить AWB/booking, flight, cargo manifest, terminal records и срок ответа. |
| Какие доказательства приложить? | AWB, booking, cargo manifest, акт терминала/GHA, фото, отметки и переписку. |
| Можно ли признать требования или settlement? | Только после ручного согласования юриста, финансов и страховщика. |
| Какие факты нужны для «Доверенность на представительство в суде по air cargo dispute»? | Перечислить недостающие AWB, booking, рейс, airport pair, timeline события, сумму, доказательства вручения и ответственных. |

## Ответственные роли

| Роль | Зона ответственности |
|------|----------------------|
| Руководитель юридического отдела | утверждает позицию по профилю «представительство в суде», settlement authority, waiver и спорные liability caps |
| Litigation authority owner | ведет chronology, evidence bundle, срок ответа и коммуникацию по событию: hearing date, filing deadline или enforcement action |
| Air cargo operations / GHA contact | подтверждает для «Доверенность на представительство в суде по air cargo dispute» movement, acceptance/offload/release, terminal act, handling records и operational root cause |
| Finance / insurer / broker contact | сверяет по «Доверенность на представительство в суде по air cargo dispute» сумму требования, reserve, оплату, customs costs, insurance notice и право регресса |

## Риски и ограничения

- Нельзя направлять документ без evidence по профилю «представительство в суде»: court file, claim draft,
  evidence bundle, AWB/HAWB, calculation, proof of service, authority approvals.
- Ключевое ограничение: нельзя включать право признания иска, отказа или мирового соглашения без explicit
  approval.
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

- ГК РФ, ст. 185-189 (доверенность)
- Воздушный кодекс РФ
- АПК РФ

## Критерии качества ответа

- ответ относится к профилю «представительство в суде» и не подменяет его общей претензионной процедурой
- доказательства названы предметно: court file, claim draft, evidence bundle, AWB/HAWB, calculation, proof of
  service, authority approvals
- отдельно указано ограничение или gap: нельзя включать право признания иска, отказа или мирового соглашения без
  explicit approval
- срок ответа, способ вручения, escalation route и safe legal position отражены явно

## Контрольный список

- [ ] карточка спора сопоставлена с документом «Доверенность на представительство в суде по air cargo dispute» и
  профилем «представительство в суде»
- [ ] собран evidence bundle: court file, claim draft, evidence bundle, AWB/HAWB, calculation, proof of service,
  authority approvals
- [ ] проверены claim notice, limitation period, proof of delivery/service и authority signer
- [ ] оценено ограничение: нельзя включать право признания иска, отказа или мирового соглашения без explicit
  approval
- [ ] текст не признает долг, вину, causation, размер ущерба или waiver без отдельного approval

## Порядок пересмотра и актуализации

Владелец документа: Руководитель юридического отдела. Плановый пересмотр проводится не реже одного раза в 12
месяцев.

Внеплановый пересмотр нужен после события: hearing date, filing deadline или enforcement action; также после
нового claim pattern, изменения carrier/GHA rules, customs practice, insurance wording, limitation period или
судебной практики.

При пересмотре Legal проверяет закрытые дела профиля «представительство в суде»: какие evidence сработали, какие
сроки были сорваны, где RAG-ответ требовал safe-position предупреждения.

## История изменений

| Версия | Дата | Изменение | Автор |
|--------|------|-----------|-------|
| 1.0 | 2026-05-15 | Первичная редакция внутреннего документа | Владелец процесса |

> Применять «Доверенность на представительство в суде по air cargo dispute» после подтверждения владельцем процесса; спорные и нетиповые кейсы требуют ручной проверки.
