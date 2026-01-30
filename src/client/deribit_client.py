import aiohttp
import asyncio
from typing import Optional, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DeribitClient:
    """Асинхронный клиент для API Deribit"""
    
    def __init__(self, base_url: str = "https://test.deribit.com"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    def _get_instrument_name(self, ticker: str) -> str:
        """Конвертирует btc_usd в BTC-PERPETUAL или ETH-PERPETUAL"""
        currency = ticker.upper().split('_')[0]
        return f"{currency}-PERPETUAL"
            
    async def get_ticker_price(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Получает текущую цену с Deribit API используя метод ticker.
        
        Args:
            ticker: Тикер в формате 'btc_usd' или 'eth_usd'
            
        Returns:
            Словарь с ценой и timestamp или None
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        # Получаем правильное имя инструмента
        instrument_name = self._get_instrument_name(ticker)
        url = f"{self.base_url}/api/v2/public/ticker"
        params = {"instrument_name": instrument_name}
        
        try:
            logger.debug(f"Запрос цены для {ticker} (instrument: {instrument_name})")
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if "error" in data:
                        logger.error(f"Ошибка API для {ticker}: {data['error']}")
                        return None
                    
                    result = data.get("result", {})
                    logger.debug(f"Ответ API для {ticker}: {result}")
                    
                    # Получаем последнюю цену (last_price)
                    price = result.get("last_price")
                    if price is None:
                        # Если нет last_price, берем mark_price или index_price
                        price = result.get("mark_price") or result.get("index_price")
                    
                    # Получаем timestamp (timestamp в миллисекундах)
                    timestamp = result.get("timestamp")
                    
                    if price is not None:
                        # Конвертируем timestamp в секунды
                        if timestamp:
                            timestamp = timestamp // 1000  # мс -> с
                        else:
                            timestamp = int(datetime.now().timestamp())
                        
                        logger.info(f"✅ Получена цена {ticker}: {price}, timestamp: {timestamp}")
                        return {
                            "ticker": ticker,
                            "price": float(price),
                            "timestamp": timestamp
                        }
                    else:
                        logger.error(f"Цена не найдена в ответе для {ticker}")
                        # Детальный лог для отладки
                        logger.debug(f"Полный ответ: {result}")
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка HTTP {response.status} для {ticker}: {error_text}")
                    
        except asyncio.TimeoutError:
            logger.error(f"Таймаут запроса для {ticker}")
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка сети для {ticker}: {e}")
        except Exception as e:
            logger.error(f"Неожиданная ошибка для {ticker}: {e}")
            
        return None
    
    async def get_multiple_prices(self, tickers: list) -> Dict[str, Optional[Dict]]:
        """Параллельное получение цен для нескольких тикеров"""
        if not tickers:
            return {}
            
        tasks = [self.get_ticker_price(ticker) for ticker in tickers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        price_dict = {}
        for ticker, result in zip(tickers, results):
            if isinstance(result, Exception):
                logger.error(f"Ошибка для {ticker}: {result}")
                price_dict[ticker] = None
            else:
                price_dict[ticker] = result
                
        return price_dict

async def fetch_price(ticker: str) -> Optional[Dict]:
    """Упрощенная функция для получения одной цены"""
    async with DeribitClient() as client:
        return await client.get_ticker_price(ticker)

async def fetch_prices(tickers: list) -> Dict[str, Optional[Dict]]:
    """Упрощенная функция для получения нескольких цен"""
    async with DeribitClient() as client:
        return await client.get_multiple_prices(tickers)

if __name__ == "__main__":
    """Тестирование клиента"""
    import sys
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    async def test():
        print("🧪 Тестирование DeribitClient с методом ticker...")
        
        # Тест 1: Получение BTC цены
        print("\n1. Получение BTC цены:")
        btc_price = await fetch_price("btc_usd")
        if btc_price:
            print(f"✅ BTC: ${btc_price['price']} (timestamp: {btc_price['timestamp']})")
        else:
            print("❌ Не удалось получить BTC цену")
        
        # Тест 2: Получение ETH цены
        print("\n2. Получение ETH цены:")
        eth_price = await fetch_price("eth_usd")
        if eth_price:
            print(f"✅ ETH: ${eth_price['price']} (timestamp: {eth_price['timestamp']})")
        else:
            print("❌ Не удалось получить ETH цену")
        
        # Тест 3: Параллельное получение
        print("\n3. Параллельное получение BTC и ETH:")
        prices = await fetch_prices(["btc_usd", "eth_usd"])
        for ticker, price_data in prices.items():
            if price_data:
                print(f"✅ {ticker}: ${price_data['price']}")
            else:
                print(f"❌ {ticker}: не получено")
    
    asyncio.run(test())
