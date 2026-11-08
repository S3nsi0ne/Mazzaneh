import asyncio
import logging
import time
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    InlineQuery, InlineQueryResultArticle, InputTextMessageContent
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.config import BOT_TOKEN, CHANNEL_ID
from src.fetcher import fetch_prices
from src.formatter import build_channel_message, format_price

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

live_message_id: int | None = None
last_sent_text: str = ""

# لینک نمودارهای آماده در مخزن نبض
CHARTS = {
    "chart_usd": ("نمودار تغییرات دلار آزاد 💵", "https://raw.githubusercontent.com/itsyebekhe/nabz/main/usd_chart.png"),
    "chart_eur": ("نمودار تغییرات یورو 💶", "https://raw.githubusercontent.com/itsyebekhe/nabz/main/eur_chart.png"),
    "chart_gold": ("نمودار طلای ۱۸ عیار ✨",
                   "https://raw.githubusercontent.com/itsyebekhe/nabz/main/gold_18k_chart.png"),
    "chart_coin": ("نمودار سکه امامی 🪙", "https://raw.githubusercontent.com/itsyebekhe/nabz/main/coin_emami_chart.png"),
}


def get_price_keyboard() -> InlineKeyboardMarkup:
    """ساخت دکمه‌های شیشه‌ای زیر پیام قیمت"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📈 چارت دلار", callback_data="chart_usd"),
            InlineKeyboardButton(text="📈 چارت طلا ۱۸", callback_data="chart_gold"),
        ],
        [
            InlineKeyboardButton(text="📈 چارت سکه", callback_data="chart_coin"),
            InlineKeyboardButton(text="📈 چارت یورو", callback_data="chart_eur"),
        ],
        [
            InlineKeyboardButton(text="🔄 بروزرسانی لحظه‌ای", callback_data="refresh_price")
        ]
    ])


async def update_channel_board(force_new: bool = False):
    """دریافت قیمت جدید و بروزرسانی پیام سنجاق‌شده در کانال"""
    global live_message_id, last_sent_text

    if force_new:
        live_message_id = None
        last_sent_text = ""

    data = await fetch_prices()
    if not data:
        logging.warning("عدم دریافت اطلاعات از منبع نبض")
        return

    new_text = build_channel_message(data, channel_id=CHANNEL_ID)

    if new_text == last_sent_text and live_message_id is not None:
        return

    try:
        if live_message_id is None:
            msg = await bot.send_message(chat_id=CHANNEL_ID, text=new_text, reply_markup=get_price_keyboard())
            live_message_id = msg.message_id
            try:
                await bot.pin_chat_message(
                    chat_id=CHANNEL_ID,
                    message_id=live_message_id,
                    disable_notification=True
                )
            except Exception as pin_err:
                logging.warning(f"پیام پین نشد: {pin_err}")
            logging.info(f"✅ تابلو زنده در کانال ساخته شد (Message ID: {live_message_id})")
        else:
            await bot.edit_message_text(
                chat_id=CHANNEL_ID,
                message_id=live_message_id,
                text=new_text,
                reply_markup=get_price_keyboard()
            )
            logging.info("🔄 تابلو زنده کانال بروزرسانی شد.")

        last_sent_text = new_text
    except Exception as e:
        error_msg = str(e).lower()
        if "message to edit not found" in error_msg or "message_id_invalid" in error_msg:
            logging.warning("⚠️ پیام قبلی در کانال پیدا نشد (پاک شده است). در حال ارسال پیام جدید...")
            live_message_id = None
            last_sent_text = ""
            await update_channel_board(force_new=True)
        else:
            logging.error(f"❌ خطا در ارسال/ویرایش پیام کانال: {e}")


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "سلام! به بات <b>مظنه | نبض بازار</b> خوش آمدید 📊\n\n"
        "🔹 <b>دستورات کاربردی:</b>\n"
        "• /price — دریافت تابلو لحظه‌ای ارز، طلا و حباب سکه\n"
        "• /gold <code>[وزن] [درصد اجرت]</code> — ماشین‌حساب خرید طلا (مثال: <code>/gold 4.5 14</code>)\n"
        "• /repost — ارسال و پین مجدد تابلو در کانال\n\n"
        "💡 <i>همچنین می‌توانید در هر چتی آیدی بات را به همراه یک عدد تایپ کنید تا معادل تومانی آن را لحظه‌ای حساب کند!</i>"
    )


@dp.message(Command("price"))
async def cmd_price(message: Message):
    wait_msg = await message.answer("⏳ در حال دریافت آخرین نرخ‌های بازار...")
    data = await fetch_prices()
    if data:
        text = build_channel_message(data, channel_id=CHANNEL_ID)
        await wait_msg.edit_text(text, reply_markup=get_price_keyboard())
    else:
        await wait_msg.edit_text("❌ خطا در دریافت اطلاعات از سرور.")


@dp.message(Command("repost"))
async def cmd_repost(message: Message):
    await update_channel_board(force_new=True)
    await message.answer("✅ تابلو جدید مجدداً در کانال ارسال و سنجاق شد!")


@dp.message(Command("gold"))
async def cmd_gold_calc(message: Message):
    """ماشین حساب طلا: /gold [وزن به گرم] [اجرت کل به درصد]"""
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer(
            "⚖️ <b>ماشین‌حساب خرید طلا</b>\n\n"
            "لطفاً وزن طلا (به گرم) و درصد اجرت/سود (اختیاری، پیش‌فرض ۱۶٪) را بعد از دستور وارد کنید.\n"
            "مثال برای ۴.۵ گرم طلا با ۱۴ درصد اجرت و سود:\n"
            "<code>/gold 4.5 14</code>"
        )
        return

    try:
        weight = float(parts[1])
        fee_pct = float(parts[2]) if len(parts) > 2 else 16.0
    except ValueError:
        await message.answer("❌ لطفاً وزن و درصد را به صورت عدد انگلیسی وارد کنید (مثال: <code>/gold 3.2 15</code>).")
        return

    data = await fetch_prices()
    if not data or not data.get("gold_18k"):
        await message.answer("❌ خطا در دریافت نرخ لحظه‌ای طلا.")
        return

    gold_18k = float(data["gold_18k"])
    raw_price = weight * gold_18k
    final_price = raw_price * (1 + (fee_pct / 100))

    await message.answer(
        f"🧮 <b>فاکتور محاسبه طلای ۱۸ عیار:</b>\n\n"
        f"• وزن طلا: <code>{weight}</code> گرم\n"
        f"• نرخ هر گرم طلای ۱۸: <code>{format_price(gold_18k)}</code> تومان\n"
        f"• ارزش طلای خام: <code>{format_price(raw_price)}</code> تومان\n"
        f"• اجرت، سود و مالیات ({fee_pct}%): <code>{format_price(final_price - raw_price)}</code> تومان\n\n"
        f"💰 <b>قیمت نهایی قابل پرداخت:</b> <code>{format_price(final_price)}</code> تومان"
    )


@dp.callback_query(F.data == "refresh_price")
async def cb_refresh_price(callback: CallbackQuery):
    data = await fetch_prices()
    if not data:
        await callback.answer("خطا در دریافت اطلاعات!", show_alert=True)
        return
    new_text = build_channel_message(data, channel_id=CHANNEL_ID)
    try:
        await callback.message.edit_text(new_text, reply_markup=get_price_keyboard())
        await callback.answer("✅ قیمت‌ها بروزرسانی شد")
    except Exception:
        await callback.answer("قیمت‌ها تغییری نکرده است ✅")


@dp.callback_query(F.data.startswith("chart_"))
async def cb_send_chart(callback: CallbackQuery):
    chart_info = CHARTS.get(callback.data)
    if not chart_info:
        return
    title, url = chart_info
    await callback.answer("در حال دریافت نمودار...")
    fresh_url = f"{url}?t={int(time.time())}"
    await callback.message.answer_photo(photo=fresh_url, caption=f"📊 <b>{title}</b>\n📢 {CHANNEL_ID}")


@dp.inline_query()
async def inline_calculator(query: InlineQuery):
    """ماشین حساب سریع در حالت اینلاین"""
    text = query.query.strip()
    try:
        amount = float(text) if text else 1.0
    except ValueError:
        return

    data = await fetch_prices()
    if not data:
        return

    usd_total = amount * float(data.get("usd", 0))
    eur_total = amount * float(data.get("eur", 0))
    gold_total = amount * float(data.get("gold_18k", 0))

    results = [
        InlineQueryResultArticle(
            id="usd_calc",
            title=f"💵 {amount:g} دلار آمریکا = {format_price(usd_total)} تومان",
            description=f"نرخ واحد: {format_price(data.get('usd', 0))} تومان",
            input_message_content=InputTextMessageContent(
                message_text=f"💵 <b>{amount:g} دلار آمریکا:</b> <code>{format_price(usd_total)}</code> تومان\n(نرخ واحد: {format_price(data.get('usd', 0))} تومان)\n📢 {CHANNEL_ID}"
            )
        ),
        InlineQueryResultArticle(
            id="eur_calc",
            title=f"💶 {amount:g} یورو = {format_price(eur_total)} تومان",
            description=f"نرخ واحد: {format_price(data.get('eur', 0))} تومان",
            input_message_content=InputTextMessageContent(
                message_text=f"💶 <b>{amount:g} یورو:</b> <code>{format_price(eur_total)}</code> تومان\n(نرخ واحد: {format_price(data.get('eur', 0))} تومان)\n📢 {CHANNEL_ID}"
            )
        ),
        InlineQueryResultArticle(
            id="gold_calc",
            title=f"✨ {amount:g} گرم طلای ۱۸ عیار = {format_price(gold_total)} تومان",
            description=f"نرخ هر گرم: {format_price(data.get('gold_18k', 0))} تومان",
            input_message_content=InputTextMessageContent(
                message_text=f"✨ <b>{amount:g} گرم طلای ۱۸ عیار:</b> <code>{format_price(gold_total)}</code> تومان\n(نرخ هر گرم: {format_price(data.get('gold_18k', 0))} تومان)\n📢 {CHANNEL_ID}"
            )
        ),
    ]
    await query.answer(results, cache_time=30)


async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_channel_board, "interval", minutes=3)
    scheduler.start()

    await update_channel_board()
    logging.info("🚀 بات مظنه با موفقیت روشن شد...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())