import aiohttp
import asyncio
import sys
from datetime import datetime, timedelta
import json

class CurrencyRateFetcher:
    BASE_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date="

    def __init__(self, days):
        self.days = days
        self.validate_days()

    def validate_days(self):
        if not (1 <= self.days <= 10):
            raise ValueError("The number of days must be between 1 and 10.")

    async def fetch_rates_for_date(self, session, date):
        url = self.BASE_URL + date.strftime('%d.%m.%Y')
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return self.parse_rates(data, date)
                else:
                    raise ValueError(f"Failed to fetch data for {date.strftime('%d.%m.%Y')}, status: {response.status}")
        except Exception as e:
            print(f"Error fetching data for {date.strftime('%d.%m.%Y')}: {e}")
            return None

    def parse_rates(self, data, date):
        rates = {"EUR": None, "USD": None}
        for rate in data.get('exchangeRate', []):
            if rate.get('currency') in rates:
                rates[rate['currency']] = {
                    'sale': rate.get('saleRate'),
                    'purchase': rate.get('purchaseRate')
                }
        return {date.strftime('%d.%m.%Y'): rates}

    async def fetch_all_rates(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(self.days):
                date = datetime.now() - timedelta(days=i)
                tasks.append(self.fetch_rates_for_date(session, date))
            return await asyncio.gather(*tasks)

async def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <number_of_days>")
        return

    try:
        days = int(sys.argv[1])
        fetcher = CurrencyRateFetcher(days)
        results = await fetcher.fetch_all_rates()

        
        rates = [result for result in results if result is not None]
        print(json.dumps(rates, indent=2, ensure_ascii=False))

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())