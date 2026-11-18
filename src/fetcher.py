import asyncio
import logging

import aiohttp
from aiohttp import ClientTimeout

from src.config import NABZ_API_URL

logger = logging.getLogger(__name__)

_TIMEOUT = ClientTimeout(total=15, connect=5)


async def fetch_prices() -> dict | list | None:
    """دریافت اطلاعات لحظه‌ای قیمت‌ها از منبع نبض"""
    for attempt in range(3):
        try:
            async with aiohttp.ClientSession(timeout=_TIMEOUT) as session:
                async with session.get(NABZ_API_URL) as response:
                    if response.status == 200:
                        return await response.json(content_type=None)
                    logger.warning("Nabz returned HTTP %s (attempt %d)", response.status, attempt + 1)
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            logger.warning("Fetch attempt %d failed: %s", attempt + 1, exc)

        if attempt < 2:
            await asyncio.sleep(0.5 * (2 ** attempt))

    logger.error("Failed to fetch prices after 3 attempts")
    return None


if __name__ == "__main__":
    async def test():
        data = await fetch_prices()
        if data:
            print("✅ اطلاعات با موفقیت دریافت شد!")
            import json
            print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
        else:
            print("❌ دریافت اطلاعات ناموفق بود.")

    asyncio.run(test())