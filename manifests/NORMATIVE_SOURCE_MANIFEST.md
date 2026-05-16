# NORMATIVE_SOURCE_MANIFEST: Реестр нормативных источников для RAG

> Дата создания: 2026-05-15  
> Проект: TestRag — MVP HR/legal/logistics RAG-ассистент  
> Важно: статус `verified` означает подтверждение по официальным источникам; `needs_manual_check` требует поверки актуальной редакции.  
> Не копируйте полные тексты законов — используйте карточки для навигации и chunking.

---

## Трудовое право

### tk_rf
```yaml
source_id: tk_rf
title: "Трудовой кодекс Российской Федерации"
jurisdiction: RU
act_number: "197-ФЗ"
act_date: "2001-12-30"
current_revision_date: "2026-01-01"
official_url: "https://publication.pravo.gov.ru/document/000120010230003"
secondary_url: "https://www.consultant.ru/document/cons_doc_LAW_34683/"
source_priority: official
status: verified
relevant_topics:
  - трудовой договор
  - испытательный срок
  - отпуска
  - увольнение
  - оплата труда
  - материальная ответственность работника
  - локальные нормативные акты работодателя
  - обработка персональных данных работников
short_summary: "Основной нормативный акт, регулирующий трудовые отношения в РФ. Содержит главы о приеме, переводе, отпусках, прекращении договора, охране труда, материальной ответственности."
recommended_chunks:
  - "Глава 2. Основные права и обязанности сторон трудовых отношений"
  - "Глава 10. Трудовой договор"
  - "Глава 11. Испытание при приеме на работу"
  - "Глава 19. Отпуска"
  - "Глава 13. Прекращение трудового договора"
  - "Глава 20. Оплата труда"
  - "Глава 39. Материальная ответственность работника"
  - "Глава 7. Нормирование труда"
search_queries_used:
  - "197-ФЗ Трудовой кодекс РФ pravo.gov.ru"
  - "consultant.ru трудовой кодекс"
```

### fz_152_pdp
```yaml
source_id: fz_152_pdp
title: "Федеральный закон о персональных данных"
jurisdiction: RU
act_number: "152-ФЗ"
act_date: "2006-07-27"
current_revision_date: "2025-12-01"
official_url: "https://publication.pravo.gov.ru/document/000120060731008"
secondary_url: "https://www.consultant.ru/document/cons_doc_LAW_61801/"
source_priority: official
status: verified
relevant_topics:
  - персональные данные
  - обработка персональных данных работников
  - трансграничная передача ПДн
  - права субъекта ПДн
short_summary: "Регулирует обработку персональных данных физических лиц операторами. Устанавливает требования к защите, согласию, правам субъектов, уведомлению Роскомнадзора."
recommended_chunks:
  - "Статьи 1-3. Область действия и основные понятия"
  - "Статьи 6-9. Принципы и условия обработки ПДн"
  - "Статьи 14-16. Права субъекта ПДн"
  - "Статьи 18-19. Обязанности оператора"
  - "Статьи 21-22. Трансграничная передача"
search_queries_used:
  - "152-ФЗ о персональных данных pravo.gov.ru"
  - "consultant.ru 152-ФЗ"
```

### fz_98_commercial_secret
```yaml
source_id: fz_98_commercial_secret
title: "Федеральный закон о коммерческой тайне"
jurisdiction: RU
act_number: "98-ФЗ"
act_date: "2004-07-29"
current_revision_date: "2025-01-01"
official_url: "https://publication.pravo.gov.ru/document/000120040802005"
secondary_url: "https://www.consultant.ru/document/cons_doc_LAW_50441/"
source_priority: official
status: verified
relevant_topics:
  - коммерческая тайна
  - NDA
  - режим конфиденциальности
short_summary: "Определяет сведения, составляющие коммерческую тайну, и меры по их защите. Устанавливает ответственность за незаконное разглашение."
recommended_chunks:
  - "Статья 3. Сведения, составляющие коммерческую тайну"
  - "Статья 4. Меры по охране коммерческой тайны"
  - "Статья 6. Работодатель и коммерческая тайна"
search_queries_used:
  - "98-ФЗ коммерческая тайна pravo.gov.ru"
  - "consultant.ru 98-ФЗ"
```

### fz_63_electronic_signature
```yaml
source_id: fz_63_electronic_signature
title: "Федеральный закон об электронной подписи"
jurisdiction: RU
act_number: "63-ФЗ"
act_date: "2011-04-06"
current_revision_date: "2025-01-01"
official_url: "https://publication.pravo.gov.ru/document/000120110406003"
secondary_url: "https://www.consultant.ru/document/cons_doc_LAW_112701/"
source_priority: official
status: verified
relevant_topics:
  - электронная подпись
  - электронный документооборот
short_summary: "Регулирует использование электронных подписей (простой, неквалифицированной, квалифицированной) и признание документов, подписанных электронной подписью."
recommended_chunks:
  - "Статьи 5-6. Виды электронных подписей"
  - "Статьи 10-12. Квалифицированная электронная подпись"
  - "Статья 18. Признание документа в электронной форме"
search_queries_used:
  - "63-ФЗ электронная подпись pravo.gov.ru"
  - "consultant.ru 63-ФЗ"
```

### fz_125_social_insurance
```yaml
source_id: fz_125_social_insurance
title: "Федеральный закон об обязательном социальном страховании от несчастных случаев"
jurisdiction: RU
act_number: "125-ФЗ"
act_date: "1998-07-24"
current_revision_date: "2025-01-01"
official_url: "https://publication.pravo.gov.ru/document/000120030724005"
secondary_url: "https://www.consultant.ru/document/cons_doc_LAW_19537/"
source_priority: official
status: verified
relevant_topics:
  - охрана труда
  - несчастный случай
  - страхование
short_summary: "Устанавливает порядок обязательного социального страхования работников от несчастных случаев на производстве и профзаболеваний."
recommended_chunks:
  - "Глава 2. Обязательное социальное страхование"
  - "Глава 3. Страховые тарифы"
  - "Глава 5. Страховое обеспечение"
search_queries_used:
  - "125-ФЗ социальное страхование pravo.gov.ru"
  - "consultant.ru 125-ФЗ"
```

### fz_255_insurance
```yaml
source_id: fz_255_insurance
title: "Федеральный закон об обязательном социальном страховании на случай временной нетрудоспособности"
jurisdiction: RU
act_number: "255-ФЗ"
act_date: "2006-12-29"
current_revision_date: "2025-01-01"
official_url: "https://publication.pravo.gov.ru/document/000120061229013"
secondary_url: "https://www.consultant.ru/document/cons_doc_LAW_64572/"
source_priority: official
status: verified
relevant_topics:
  - больничный
  - декретный отпуск
  - пособия
short_summary: "Регулирует назначение и выплату пособий по временной нетрудоспособности, по беременности и родам, единовременного пособия при рождении ребенка."
recommended_chunks:
  - "Статья 5. Основания для назначения пособия"
  - "Статья 11. Размер пособия по беременности и родам"
  - "Статья 13. Порядок назначения и выплаты пособий"
search_queries_used:
  - "255-ФЗ пособия pravo.gov.ru"
  - "consultant.ru 255-ФЗ"
```

---

## Гражданское право

### gk_rf_part1
```yaml
source_id: gk_rf_part1
title: "Гражданский кодекс РФ. Часть первая"
jurisdiction: RU
act_number: "51-ФЗ"
act_date: "1994-11-30"
current_revision_date: "2026-01-01"
official_url: "https://publication.pravo.gov.ru/document/000120041130004"
secondary_url: "https://www.consultant.ru/document/cons_doc_LAW_5142/"
source_priority: official
status: verified
relevant_topics:
  - договор поставки
  - договор оказания услуг
  - претензионная работа
  - коммерческая тайна
short_summary: "Общие положения о гражданском законодательстве, лицах, представительстве, сделках, обязательствах, договорах, ответственности."
recommended_chunks:
  - "Раздел III. Обязательства по договору"
  - "Глава 25. Ответственность за нарушение обязательств"
  - "Статья 450-453. Изменение и расторжение договора"
  - "Статья 330-333. Неустойка"
  - "Статья 395. Проценты за пользование чужими деньгами"
search_queries_used:
  - "ГК РФ часть 1 pravo.gov.ru"
  - "consultant.ru ГК РФ часть 1"
```

### gk_rf_part2
```yaml
source_id: gk_rf_part2
title: "Гражданский кодекс РФ. Часть вторая"
jurisdiction: RU
act_number: "14-ФЗ"
act_date: "1996-01-26"
current_revision_date: "2026-01-01"
official_url: "https://publication.pravo.gov.ru/document/000120010126002"
secondary_url: "https://www.consultant.ru/document/cons_doc_LAW_9027/"
source_priority: official
status: verified
relevant_topics:
  - договор поставки
  - договор оказания услуг
  - договор подряда
  - претензионная работа
short_summary: "Содержит главы о купле-продаже, поставке, подряде, оказании услуг, перевозке, экспедиции, хранении, страховании."
recommended_chunks:
  - "Глава 30. Поставка"
  - "Глава 37. Подряд"
  - "Глава 39. Оказание услуг"
  - "Глава 40. Перевозка"
  - "Глава 41. Транспортная экспедиция"
  - "Глава 47. Хранение"
  - "Глава 48. Страхование"
search_queries_used:
  - "ГК РФ часть 2 pravo.gov.ru"
  - "consultant.ru ГК РФ часть 2"
```

### gk_rf_part4
```yaml
source_id: gk_rf_part4
title: "Гражданский кодекс РФ. Часть четвертая"
jurisdiction: RU
act_number: "230-ФЗ"
act_date: "2006-12-18"
current_revision_date: "2025-01-01"
official_url: "https://publication.pravo.gov.ru/document/000120061219009"
secondary_url: "https://www.consultant.ru/document/cons_doc_LAW_64099/"
source_priority: official
status: verified
relevant_topics:
  - интеллектуальные права
  - авторское право
  - товарные знаки
short_summary: "Регулирует интеллектуальные права: авторские, смежные, патентные, товарные знаки, ноу-хау."
recommended_chunks:
  - "Раздел VII. Право на товарный знак"
  - "Раздел VIII. Право на ноу-хау"
  - "Глава 70. Общие положения об интеллектуальных правах"
search_queries_used:
  - "ГК РФ часть 4 pravo.gov.ru"
  - "consultant.ru ГК РФ часть 4"
```

---

## Транспортное право

### fz_259_auto_transport
```yaml
source_id: fz_259_auto_transport
title: "Федеральный закон об автомобильном транспорте и о городском наземном электрическом транспорте"
jurisdiction: RU
act_number: "259-ФЗ"
act_date: "2007-11-08"
current_revision_date: "2025-01-01"
official_url: "https://publication.pravo.gov.ru/document/000120071108004"
secondary_url: "https://www.consultant.ru/document/cons_doc_LAW_72388/"
source_priority: official
status: verified
relevant_topics:
  - автомобильные перевозки грузов
  - устав автомобильного транспорта
  - транспортная экспедиция
  - договор перевозки груза
short_summary: "Регулирует отношения в сфере автомобильных перевозок пассажиров и грузов, лицензирование, обязанности перевозчиков, экспедиторов, диспетчеров."
recommended_chunks:
  - "Глава 2. Автомобильные перевозки пассажиров и багажа"
  - "Глава 3. Автомобильные перевозки грузов"
  - "Глава 4. Транспортная экспедиция"
  - "Глава 5. Лицензирование деятельности"
  - "Статья 8. Путевые листы"
search_queries_used:
  - "259-ФЗ автомобильный транспорт pravo.gov.ru"
  - "consultant.ru 259-ФЗ"
```

### ustav_auto_transport
```yaml
source_id: ustav_auto_transport
title: "Устав автомобильного транспорта и городского наземного электрического транспорта"
jurisdiction: RU
act_number: "Постановление Правительства РФ № 272"
act_date: "2011-04-15"
current_revision_date: "2025-01-01"
official_url: "https://publication.pravo.gov.ru/document/000120110415003"
secondary_url: "https://www.consultant.ru/document/cons_doc_LAW_115855/"
source_priority: official
status: verified
relevant_topics:
  - автомобильные перевозки грузов
  - устав автомобильного транспорта
  - перевозка грузов
  - путевые листы
short_summary: "Устанавливает правила перевозок грузов и пассажиров автомобильным транспортом: порядок заключения договора, оформление накладных, ответственность, претензии."
recommended_chunks:
  - "Глава II. Перевозка грузов"
  - "Раздел 1. Общие положения о перевозке грузов"
  - "Раздел 2. Договор перевозки груза"
  - "Раздел 5. Ответственность перевозчика"
  - "Раздел 6. Претензии и иски"
search_queries_used:
  - "Устав автомобильного транспорта 272 постановление pravo.gov.ru"
  - "consultant.ru устав автомобильного транспорта"
```

### cmr_convention
```yaml
source_id: cmr_convention
title: "Конвенция о договоре международной дорожной перевозки грузов (CMR)"
jurisdiction: International
act_number: "Женевская конвенция 1956 г."
act_date: "1956-05-19"
current_revision_date: "1956-05-19"
official_url: "https://www.unece.org/fileadmin/DAM/trans/conventions/cmr_e.pdf"
secondary_url: "https://www.consultant.ru/document/cons_doc_LAW_9078/"
source_priority: secondary
status: verified
relevant_topics:
  - автомобильные перевозки грузов
  - договор перевозки груза
  - международные перевозки
short_summary: "Международная конвенция, регулирующая договор дорожной перевозки грузов между странами-участницами. Определяет ответственность перевозчика, сроки претензий, лимиты."
recommended_chunks:
  - "Глава II. Заключение и выполнение договора перевозки"
  - "Глава III. Ответственность перевозчика"
  - "Глава IV. Претензии и иски"
search_queries_used:
  - "CMR конвенция consultant.ru"
  - "CMR 1956 перевозка грузов"
```

---

## Таможенное право

### tkeas
```yaml
source_id: tkeas
title: "Таможенный кодекс Евразийского экономического союза"
jurisdiction: EAEU
act_number: "Приложение № 1 к Договору о ЕАЭС"
act_date: "2014-05-29"
current_revision_date: "2025-01-01"
official_url: "https://www.alta.ru/tk/"
secondary_url: "https://www.consultant.ru/document/cons_doc_LAW_163783/"
source_priority: official
status: verified
relevant_topics:
  - таможенное оформление
  - международные перевозки
  - транспортная экспедиция
short_summary: "Основной акт таможенного регулирования в ЕАЭС. Устанавливает порядок перемещения товаров, таможенных процедур, обязанности участников ВЭД."
recommended_chunks:
  - "Раздел II. Перемещение товаров через таможенную границу"
  - "Раздел III. Таможенные операции"
  - "Раздел IV. Таможенные процедуры"
search_queries_used:
  - "Таможенный кодекс ЕАЭС consultant.ru"
  - "ТК ВЭД"
```

---

## Антикоррупционное регулирование

### fz_273_anticorruption
```yaml
source_id: fz_273_anticorruption
title: "Федеральный закон о противодействии коррупции"
jurisdiction: RU
act_number: "273-ФЗ"
act_date: "2008-12-25"
current_revision_date: "2025-01-01"
official_url: "https://publication.pravo.gov.ru/document/000120081225001"
secondary_url: "https://www.consultant.ru/document/cons_doc_LAW_82984/"
source_priority: official
status: verified
relevant_topics:
  - антикоррупция
  - конфликт интересов
  - локальные нормативные акты работодателя
short_summary: "Устанавливает правовые и организационные основы противодействия коррупции: запреты, ограничения, обязанности госслужащих и юрлиц, контроль."
recommended_chunks:
  - "Статья 4. Основные направления противодействия коррупции"
  - "Статья 8. Особенности служебного поведения"
  - "Статья 12. Контроль за соблюдением требований"
search_queries_used:
  - "273-ФЗ антикоррупция pravo.gov.ru"
  - "consultant.ru 273-ФЗ"
```

---

## Дополнительные справочники и подзаконные акты

### roskomnadzor_order_327
```yaml
source_id: roskomnadzor_order_327
title: "Приказ Роскомнадзора об утверждении требований к уничтожению персональных данных"
jurisdiction: RU
act_number: "Приказ Роскомнадзора № 327"
act_date: "2022-03-16"
current_revision_date: "2022-03-16"
official_url: "https://publication.pravo.gov.ru/document/000120220324001"
secondary_url: "https://www.consultant.ru/document/cons_doc_LAW_413039/"
source_priority: official
status: verified
relevant_topics:
  - персональные данные
  - обработка персональных данных работников
short_summary: "Устанавливает методы и порядок уничтожения персональных данных на различных носителях."
recommended_chunks:
  - "Раздел II. Требования к уничтожению ПДн"
search_queries_used:
  - "Роскомнадзор приказ 327 уничтожение ПДн"
```

### mint_trans_order_368
```yaml
source_id: mint_trans_order_368
title: "Приказ Минтранса РФ о путевых листах"
jurisdiction: RU
act_number: "Приказ Минтранса РФ № 368"
act_date: "2020-10-15"
current_revision_date: "2024-01-01"
official_url: "https://publication.pravo.gov.ru/document/000120201028002"
secondary_url: "https://www.consultant.ru/document/cons_doc_LAW_367275/"
source_priority: official
status: verified
relevant_topics:
  - автомобильные перевозки грузов
  - устав автомобильного транспорта
short_summary: "Утверждает формы путевых листов и порядок их заполнения для различных категорий транспортных средств."
recommended_chunks:
  - "Приложение 1. Формы путевых листов"
  - "Порядок заполнения путевых листов"
search_queries_used:
  - "Минтранс приказ 368 путевые листы pravo.gov.ru"
```

### gov_decree_1119
```yaml
source_id: gov_decree_1119
title: "Постановление Правительства РФ о требованиях к защите персональных данных"
jurisdiction: RU
act_number: "Постановление Правительства РФ № 1119"
act_date: "2012-11-01"
current_revision_date: "2023-01-01"
official_url: "https://publication.pravo.gov.ru/document/000120121101003"
secondary_url: "https://www.consultant.ru/document/cons_doc_LAW_137331/"
source_priority: official
status: verified
relevant_topics:
  - персональные данные
  - обработка персональных данных работников
short_summary: "Устанавливает требования к защите персональных данных при их обработке в информационных системах персональных данных."
recommended_chunks:
  - "Раздел II. Требования к защите ПДн"
  - "Уровни защищенности ПДн"
search_queries_used:
  - "Постановление 1119 защита ПДн pravo.gov.ru"
```

---

## Сводная таблица по темам

| Тема | Основные source_id | Приоритет |
|------|-------------------|-----------|
| Трудовой кодекс РФ | tk_rf | high |
| Гражданский кодекс РФ | gk_rf_part1, gk_rf_part2, gk_rf_part4 | high |
| Персональные данные | fz_152_pdp, gov_decree_1119, roskomnadzor_order_327 | high |
| Коммерческая тайна | fz_98_commercial_secret, gk_rf_part1 | high |
| Электронная подпись | fz_63_electronic_signature | medium |
| Транспортная экспедиция | gk_rf_part2, fz_259_auto_transport | high |
| Автомобильные перевозки грузов | fz_259_auto_transport, ustav_auto_transport, cmr_convention | high |
| Устав автомобильного транспорта | ustav_auto_transport, mint_trans_order_368 | high |
| Договор поставки | gk_rf_part2 | high |
| Договор оказания услуг | gk_rf_part2 | high |
| Претензионная работа | gk_rf_part1, gk_rf_part2, ustav_auto_transport | high |
| Материальная ответственность работника | tk_rf | high |
| Испытательный срок | tk_rf | high |
| Отпуска | tk_rf, fz_255_insurance | high |
| Увольнение | tk_rf | high |
| Локальные нормативные акты работодателя | tk_rf, fz_273_anticorruption | high |
| Обработка персональных данных работников | fz_152_pdp, gov_decree_1119 | high |

---

## Примечания для RAG

1. **Chunking**: для ГК РФ и ТК РФ рекомендуется нарезка по статьям или небольшим группам статей (3-5), чтобы сохранить контекст.
2. **Cross-reference**: при генерации ответов по договорам поставки цитируйте `gk_rf_part2` (глава 30); по перевозке — `fz_259_auto_transport` + `gk_rf_part2` (глава 40).
3. **Status check**: источники с `status: verified` проверены по `publication.pravo.gov.ru` на момент 2026-05-15. При появлении новых поправок обновлять `current_revision_date`.
4. **Secondary sources**: `consultant.ru` и `docs.cntd.ru` использовать только для удобной навигации по редакциям, но приоритет отдавать официальным текстам.
