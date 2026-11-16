import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from src.config import BOT_TOKEN, CHANNEL_ID
from src.fetcher import fetch_prices
from src.formatter import build_channel_message

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# منوی ساده و ثابت پی‌وی
def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 تابلو لحظه‌ای بازار")]
        ],
        resize_keyboard=True
    )

@dp.message(Command("start"))
async def cmd_start(message: Message):
    logging.info(f"دستور استارت از طرف کاربر {message.from_user.id} دریافت شد.")
    await message.answer(
        "سلام! بات با موفقیت ریست شد و الان داره کار میکنه ✅",
        reply_markup=get_main_menu()
    )

@dp.message(F.text == "📊 تابلو لحظه‌ای بازار")
async def send_board(message: Message):
    data = await fetch_prices()
    if data:
        text = build_channel_message(data, channel_id=CHANNEL_ID)
        await message.answer(text)
    else:
        await message.answer("خطا در دریافت اطلاعات بازار.")

async def main():
    logging.info("🚀 بات داره روشن میشه...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())