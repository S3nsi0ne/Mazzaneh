import asyncio
import json
import aiohttp
from src.config import NABZ_API_URL

async def fetch_prices() -> dict | list | None:
    """دریافت اطلاعات لحظه‌ای قیمت‌ها از منبع نبض"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(NABZ_API_URL, timeout=15) as response:
                if response.status == 200:
                    return await response.json(content_type=None)
                else:
                    print(f"Error: HTTP Status {response.status}")
                    return None
    except Exception as e:
        print(f"Connection error: {e}")
        return None

if __name__ == "__main__":
    async def test():
        data = await fetch_prices()
        if data:
            print("✅ اطلاعات با موفقیت دریافت شد!")
            # چاپ بخش اول دیتا برای دیدن نام دقیق کلیدها
            print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
        else:
            print("❌ دریافت اطلاعات ناموفق بود.")

    asyncio.run(test())