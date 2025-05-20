import aiohttp
import asyncio
import re
import os
import json
import random
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import time

class MarketParser:
    def __init__(self):
        self.default_configs = {
            "common": {
                "user_agents": [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
                    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
                    "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
                ],
                "headers": [
                    {
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Connection": "keep-alive",
                        "Upgrade-Insecure-Requests": "1",
                        "Referer": "https://www.wildberries.ru/",
                        "DNT": "1",
                        "Sec-Fetch-Dest": "document",
                        "Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-Site": "none",
                        "Sec-Fetch-User": "?1"
                    },
                    {
                        "Accept": "application/json",
                        "Accept-Language": "ru-RU,ru;q=0.9",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Connection": "keep-alive",
                        "Referer": "https://www.wildberries.ru/"
                    }
                ],
                "proxies": [None]
            },
            "wb": {
                "method": ["aiohttp"]
            },
            "ali": {
                "method": ["playwright"]
            },
            "ozon": {
                "method": ["playwright"]
            }
        }
        self.successful_configs = self.load_successful_configs()
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None

    def load_successful_configs(self):
        if os.path.exists("successful_configs.json"):
            try:
                with open("successful_configs.json", "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if not content:
                        return {"wb": {}, "ali": {}, "ozon": {}}
                    return json.loads(content)
            except Exception:
                return {"wb": {}, "ali": {}, "ozon": {}}
        return {"wb": {}, "ali": {}, "ozon": {}}

    def save_successful_config(self, market, config):
        try:
            self.successful_configs[market] = config
            with open("successful_configs.json", "w", encoding="utf-8") as f:
                json.dump(self.successful_configs, f, indent=4, ensure_ascii=False)
        except Exception as err:
            print(f"Ошибка сохранения конфигурации: {err}")

    async def setup_browser(self, market):
        if self.browser:
            await self.browser.close()
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-extensions',
                '--disable-component-extensions-with-background-pages',
                '--disable-default-apps',
                '--no-default-browser-check',
                '--no-first-run',
                '--window-size=1920,1080'
            ]
        )
        state_path = f"{market}_state.json"  # Файл состояния для конкретного маркетплейса
        context_args = {
            "viewport": {"width": 1920, "height": 1080},
            "user_agent": random.choice(self.default_configs["common"]["user_agents"]),
            "locale": "ru-RU",
            "timezone_id": "Europe/Moscow",
            "geolocation": {"longitude": 37.6156, "latitude": 55.7522},
            "permissions": ["geolocation"],
            "is_mobile": False,
            "has_touch": False,
            "device_scale_factor": 1.0,
            "reduced_motion": "no-preference"
        }
        if os.path.exists(state_path):
            print(f"🔁 Загружаем cookies из {state_path}")
            context_args["storage_state"] = state_path
        self.context = await self.browser.new_context(**context_args)

        # Маскируем окружение
        await self.context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => false });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        Object.defineProperty(navigator, 'languages', { get: () => ['ru-RU', 'ru', 'en-US', 'en'] });
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        """)

        await self.context.route('**', self._modify_headers)
        self.page = await self.context.new_page()
        self.page.on("response", self._handle_response)
        print("Playwright успешно настроен")
        return self.page

    async def _modify_headers(self, route):
        headers = route.request.headers
        headers.update(random.choice(self.default_configs["common"]["headers"]))
        await route.continue_(headers=headers)

    async def _handle_response(self, response):
        if 'set-cookie' in response.headers:
            print(f"🍪 Куки получены: {response.headers['set-cookie'][:60]}...")

    async def emulate_human_behavior(self):
        await asyncio.sleep(random.uniform(1.5, 3))
        for _ in range(random.randint(5, 10)):
            x, y = random.randint(100, 1000), random.randint(100, 700)
            await self.page.mouse.move(x, y, steps=random.randint(10, 20))
            await asyncio.sleep(random.uniform(0.2, 0.8))
        for _ in range(random.randint(3, 7)):
            await self.page.mouse.wheel(0, random.randint(100, 300))
            await asyncio.sleep(random.uniform(0.5, 1.5))

    async def move_slider(self, page):
        try:
            slider = await page.query_selector(".puzzle-captcha-slider .button")
            if slider:
                await slider.hover()
                await page.mouse.down()
                await page.mouse.move(100, 0, steps=10)
                await asyncio.sleep(random.uniform(0.5, 1))
                await page.mouse.up()
                await asyncio.sleep(2)
                return True
        except Exception as err:
            print(f"Ошибка при движении ползунка: {err}")
            return False

    async def fetch_with_config(self, url, headers, proxy=None, method="aiohttp", response_type="text"):
        print(f"Попытка получения данных: {url} с method={method}, proxy={proxy}")
        if method == "aiohttp":
            try:
                async with aiohttp.ClientSession() as session:
                    timeout = aiohttp.ClientTimeout(total=10, connect=5, sock_connect=5, sock_read=5)
                    async with session.get(url, headers=headers, proxy=proxy, timeout=timeout) as response:
                        response.raise_for_status()
                        if response_type == "json" or "json" in headers.get("Accept", "").lower():
                            content = await response.json()
                        else:
                            content = await response.text()
                        print(f"Успешный запрос через aiohttp: {url}")
                        return content
            except Exception as err:
                print(f"Ошибка aiohttp для {url}: {err}")
                return None
        elif method == "playwright":
            if not self.browser:
                # Определяем маркетплейс по URL
                market = "ozon" if "ozon.ru" in url else "ali" if "aliexpress.ru" in url else "wb"
                await self.setup_browser(market)
            if not self.page:
                print("Не удалось инициализировать страницу Playwright")
                return None
            try:
                await self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(random.uniform(1, 3))
                await self.page.evaluate("window.scrollBy(0, 500)")
                await asyncio.sleep(random.uniform(1, 3))

                content = await self.page.content()
                soup = BeautifulSoup(content, 'html.parser')
                if soup.select_one(".puzzle-captcha-slider"):
                    print("Обнаружена капча. Попытка решения...")
                    await asyncio.sleep(10)
                    content = await self.page.content()

                print(f"Успешный запрос через Playwright: {url}")
                return content
            except Exception as err:
                print(f"Ошибка Playwright для {url}: {err}")
                try:
                    content = await self.page.content()
                    print(f"Извлечён частичный контент: {url}")
                    return content
                except Exception as content_err:
                    print(f"Не удалось извлечь контент: {content_err}")
                    return None
        return None
    
    async def close(self, market=None):
        try:
            if self.context and market:
                state_path = f"{market}_state.json"
                print(f"💾 Сохраняем cookies в {state_path}")
                await self.context.storage_state(path=state_path)
            else:
                print("Для aiohttp не сохраняем состояние")
            if self.page: await self.page.close()
            if self.context: await self.context.close()
            if self.browser: await self.browser.close()
            if self.playwright: await self.playwright.stop()
        except Exception as err:
            print(f"Ошибка при закрытии Playwright: {err}")

class WB(MarketParser):
    async def get_price(self, url):
        """Получает цену с Wildberries."""
        market = "wb"
        print(f"Начало парсинга цены для {url}")
        if market in self.successful_configs and self.successful_configs[market]:
            config = self.successful_configs[market]
            print(f"Используем сохранённую конфигурацию: {config}")
            price = await self.fetch_price_with_config(url, config["headers"], config.get("proxy"), config["method"])
            if price:
                return price

        for attempt in range(3):
            print(f"Попытка {attempt + 1}/3 для {url}")
            # Первый проход: пробуем aiohttp
            for user_agent in self.default_configs["common"]["user_agents"]:
                for headers in self.default_configs["common"]["headers"]:
                    headers["User-Agent"] = user_agent
                    for proxy in self.default_configs["common"]["proxies"]:
                        price = await self.fetch_price_with_config(url, headers, proxy, method="aiohttp")
                        if price:
                            self.save_successful_config(market, {"headers": headers, "proxy": proxy, "method": "aiohttp"})
                            return price
            # Второй проход: пробуем playwright, если aiohttp не сработал
            for user_agent in self.default_configs["common"]["user_agents"]:
                for headers in self.default_configs["common"]["headers"]:
                    headers["User-Agent"] = user_agent
                    for proxy in self.default_configs["common"]["proxies"]:
                        price = await self.fetch_price_with_config(url, headers, proxy, method="playwright")
                        if price:
                            self.save_successful_config(market, {"headers": headers, "proxy": proxy, "method": "playwright"})
                            return price
            await asyncio.sleep(random.uniform(2, 5))

        print(f"❌ Не удалось извлечь цену с {url} для {market}")
        return None

    async def fetch_price_with_config(self, url, headers, proxy=None, method="aiohttp"):
        """Извлекает цену с заданными настройками."""
        try:
            product_id = re.search(r"\d+", url).group()
            api_url = f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={product_id}"
            data = await self.fetch_with_config(api_url, headers, proxy, method, response_type="json")
            if data:
                price = data["data"]["products"][0]["salePriceU"] / 100
                return int(price)
        except Exception as err:
            print(f"Ошибка извлечения цены для {url}: {err}")
        return None

class Ali(MarketParser):
    async def get_price(self, url):
        market = "ali"
        print(f"Начало парсинга цены для {url}")
        if market in self.successful_configs and self.successful_configs[market]:
            config = self.successful_configs[market]
            content = await self.fetch_with_config(url, config["headers"], config.get("proxy"), config["method"])
            if content:
                with open("content.txt", "w", encoding="utf-8") as f:
                    f.write(content)
                price = await self.extract_price(url, content)
                if price: return price

        for attempt in range(3):
            print(f"Попытка {attempt + 1}/3 для {url} ЯТУТУТУТУТУУТ")
            # Первый проход: пробуем playwright
            for user_agent in self.default_configs["common"]["user_agents"]:
                for headers in self.default_configs["common"]["headers"]:
                    headers["User-Agent"] = user_agent
                    for proxy in self.default_configs["common"]["proxies"]:
                        print(f"{user_agent} {headers} {proxy}")
                        await asyncio.sleep(5)
                        content = await self.fetch_with_config(url, headers, proxy, method="playwright")
                        if content:
                            with open("content.txt", "w", encoding="utf-8") as f:
                                f.write(content)
                            price = await self.extract_price(url, content)
                            if price:
                                user_agent = await self.page.evaluate("navigator.userAgent")
                                self.save_successful_config(market, {"headers": {"User-Agent": user_agent}, "proxy": proxy, "method": "playwright"})
                                return price
            await asyncio.sleep(random.uniform(2, 5))

        print(f"❌ Не удалось извлечь цену с {url} для {market}")
        return None

    async def extract_price(self, url, content):
        """Извлекает цену из HTML страницы AliExpress."""
        try:
            if content:
                price_match = re.search(r'finalPrice:(\d+\.?\d*)|activityAmount":\{"value"\:(\d+)', content)
                if price_match:
                    return int(price_match.group(1)) if price_match.group(1) else int(price_match.group(2))
                print("Цена не найдена: ", content[:1000])
            else:
                print("Контент пуст")
        except Exception as err:
            print(f"Ошибка извлечения цены для {url}: {err}")
            return None

class Ozon(MarketParser):
    async def get_price(self, url):
        market = "ozon"
        print(f"Начало парсинга цены для {url}")
        if market in self.successful_configs and self.successful_configs[market]:
            config = self.successful_configs[market]
            content = await self.fetch_with_config(url, config["headers"], config.get("proxy"), config["method"])
            if content:
                with open("ozon_content.txt", "w", encoding="utf-8") as f:
                    f.write(content)
                price = await self.extract_product_info(url, content)
                if price:
                    return price

        for attempt in range(3):
            print(f"Попытка {attempt + 1}/3 для {url}")
            # Первый проход: пробуем playwright
            for user_agent in self.default_configs["common"]["user_agents"]:
                for headers in self.default_configs["common"]["headers"]:
                    headers["User-Agent"] = user_agent
                    for proxy in self.default_configs["common"]["proxies"]:
                        content = await self.fetch_with_config(url, headers, proxy, method="playwright")
                        if content:
                            with open("ozon_content.txt", "w", encoding="utf-8") as f:
                                f.write(content)
                            price = await self.extract_product_info(url, content)
                            if price:
                                user_agent = await self.page.evaluate("navigator.userAgent")
                                self.save_successful_config(market, {"headers": {"User-Agent": user_agent}, "proxy": proxy, "method": "playwright"})
                                return price
            await asyncio.sleep(random.uniform(2, 5))

        print(f"❌ Не удалось извлечь цену с {url} для {market}")
        return None

    async def extract_product_info(self, url, content):
        try:
            if not content:
                print("Контент пуст")
            elif "Доступ ограничен" in content or "captcha" in content:
                print(f"🚫 Капча/403 обнаружена в контенте")
                return None
            else:
                price_match = re.search(r'"price":"(\d+)"', content)
                if price_match:
                    return int(price_match.group(1))
                print("Цена не найдена: ", content[:1000])
            return None
        except Exception as err:
            print(f"⚠️ Ошибка извлечения данных для {url}: {err}")
            return None