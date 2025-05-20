# Market Parser

Парсер цен с маркетплейсов Wildberries, AliExpress и Ozon. Использует `aiohttp` для Wildberries и `playwright` для AliExpress и Ozon, чтобы обходить капчи и извлекать цены.

## Возможности
- Извлечение цен с Wildberries через API.
- Парсинг AliExpress и Ozon с эмуляцией браузера.
- Автоматическое сохранение успешных конфигураций и состояния сессий.
- Обработка капчи с помощью ожидания и перезапуска браузера.

## Требования
- Python 3.8+
- Установленные зависимости (см. ниже)

## Установка

1. Склонируйте репозиторий:
   git clone https://github.com/KirillPhoenix/market-parser.git
   cd market-parser
2. Установите зависимости:
   pip install -r requirements.txt
3. Установите Playwright:
   playwright install
4. Запустите тесты tests.py:
   py tests.py
Ожидаемый вывод:
=== Итоги всех тестов ===
URL: https://www.wildberries.ru/catalog/257006351/detail.aspx -> Цена: 1838₽
URL: https://www.wildberries.ru/catalog/177736923/detail.aspx -> Цена: 777₽
URL: https://www.wildberries.ru/catalog/206275183/detail.aspx -> Цена: 1272₽
URL: https://aliexpress.ru/item/1005008252555029.html -> Цена: 1609₽
URL: https://aliexpress.ru/item/1005007501441163.html -> Цена: 5979₽
URL: https://aliexpress.ru/item/1005008427935838.html -> Цена: 203700₽
URL: https://www.ozon.ru/product/vetrovka-vesna-leto-2038630741 -> Цена: 4566₽
URL: https://www.ozon.ru/product/xiaomi-umnye-chasy-redmi-watch-5-active-51mm-chernyy-1720716328 -> Цена: 3190₽
URL: https://www.ozon.ru/product/mysh-besprovodnaya-opticheskaya-besshumnaya-do-10-metrov-chernyy-matovyy-chernyy-1402203244/ -> Цена: 299₽

## Дополнительно
Вы можете менять настройки в self.default_configs добавляя свои user-agent'ы, заголовки и прокси.
Если хотите парсить много товаров добавьте прокси или решатель капчи
