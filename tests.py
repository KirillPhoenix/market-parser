import pytest
import asyncio
from parser import WB, Ali, Ozon

ozon_links = [
    "https://www.ozon.ru/product/vetrovka-vesna-leto-2038630741",
    "https://www.ozon.ru/product/xiaomi-umnye-chasy-redmi-watch-5-active-51mm-chernyy-1720716328",
    "https://www.ozon.ru/product/mysh-besprovodnaya-opticheskaya-besshumnaya-do-10-metrov-chernyy-matovyy-chernyy-1402203244/",
]

wb_links = [
    "https://www.wildberries.ru/catalog/257006351/detail.aspx",
    "https://www.wildberries.ru/catalog/177736923/detail.aspx",
    "https://www.wildberries.ru/catalog/206275183/detail.aspx",
]

ali_links = [
    "https://aliexpress.ru/item/1005008252555029.html",
    "https://aliexpress.ru/item/1005007501441163.html",
    "https://aliexpress.ru/item/1005008427935838.html",
]

# Глобальный словарь для хранения результатов
results = {}

@pytest.mark.asyncio
async def test_wb():
    print("\n🔧 Тестируем парсер Wildberries")
    parser = WB()
    try:
        for url in wb_links:
            print(f"Тестируем URL: {url}")
            price = await parser.get_price(url)
            if isinstance(price, int) and price > 0:
                print(f"✅ {url} — {price}₽")
                results[url] = price
            else:
                print(f"❌ {url} — цена не получена")
                results[url] = "Цена не получена"
    except Exception as err:
        print(f"❌ Ошибка теста: {err}")
        for url in wb_links:
            results[url] = str(err)
    finally:
        await parser.close()
        print("Тест завершён")

@pytest.mark.asyncio
async def test_ali():
    print("\n🔧 Тестируем парсер AliExpress")
    parser = Ali()
    try:
        for url in ali_links:
            print(f"Тестируем URL: {url}")
            price = await parser.get_price(url)
            if isinstance(price, int) and price > 0:
                print(f"✅ {url} — {price}₽")
                results[url] = price
            else:
                print(f"❌ {url} — цена не получена")
                results[url] = "Цена не получена"
    except Exception as err:
        print(f"❌ Ошибка теста: {err}")
        for url in ali_links:
            results[url] = str(err)
    finally:
        await parser.close()
        print("Тест завершён")

@pytest.mark.asyncio
async def test_ozon():
    print("\n🔧 Тестируем парсер Ozon")
    parser = Ozon()
    try:
        for url in ozon_links:
            print(f"Тестируем URL: {url}")
            price = await parser.get_price(url)
            if isinstance(price, int) and price > 0:
                print(f"✅ {url} — {price}₽")
                results[url] = price
            else:
                print(f"❌ {url} — цена не получена")
                results[url] = "Цена не получена"
    except Exception as err:
        print(f"❌ Ошибка теста: {err}")
        for url in ozon_links:
            results[url] = str(err)
    finally:
        await parser.close()
        print("Тест завершён")

if __name__ == "__main__":
    asyncio.run(test_wb())
    asyncio.run(test_ali())
    asyncio.run(test_ozon())
    print("\n=== Итоги всех тестов ===")
    for url, result in results.items():
        price_output = f"{result}₽" if isinstance(result, int) else result
        print(f"URL: {url} -> Цена: {price_output}")