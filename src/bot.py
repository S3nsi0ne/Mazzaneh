import asyncio
import logging
import time
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
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


# منوی کیبورد ثابت در پی‌وی ربات
def get_main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 تابلو لحظه‌ای بازار"), KeyboardButton(text="📈 دریافت چارت‌های زنده")],
            [KeyboardButton(text="🧮 ماشین‌حساب خرید طلا"), KeyboardButton(text="🔄 تبدیل عیار آب‌شده (۷۳۰ به ۷۵۰)")]
        ],
        resize_keyboard=True
    )


def get_charts_keyboard() -> InlineKeyboardMarkup:
    """دکمه‌های شیشه‌ای چارت‌ها برای ارسال مستقیم در پی‌وی"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💵 چارت دلار", callback_data="pv_chart_usd"),
            InlineKeyboardButton(text="✨ چارت طلای ۱۸", callback_data="pv_chart_gold"),
        ],
        [
            InlineKeyboardButton(text="🪙 چارت سکه امامی", callback_data="pv_chart_coin"),
            InlineKeyboardButton(text="💶 چارت یورو", callback_data="pv_chart_eur"),
        ]
    ])


def get_channel_keyboard() -> InlineKeyboardMarkup:
    """دکمه‌های زیر پیام کانال (بروزرسانی)"""
    return InlineKeyboardMarkup(inline_keyboard=[
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
            msg = await bot.send_message(chat_id=CHANNEL_ID, text=new_text, reply_markup=get_channel_keyboard())
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
                reply_markup=get_channel_keyboard()
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
        "از منوی زیر می‌توانید به ابزارها، چارت‌های زنده و ماشین‌حساب‌های طلا و ارز دسترسی داشته باشید:",
        reply_markup=get_main_menu() # <--- این قسمت حتماً باید اینجا باشد تا کیبورد ظاهر شود
    )


@dp.message(F.text == "📊 تابلو لحظه‌ای بازار")
@dp.message(Command("price"))
async def handle_price(message: Message):
    wait_msg = await message.answer("⏳ در حال دریافت آخرین نرخ‌های بازار...")
    data = await fetch_prices()
    if data:
        text = build_channel_message(data, channel_id=CHANNEL_ID)
        await wait_msg.edit_text(text, reply_markup=get_channel_keyboard())
    else:
        await wait_msg.edit_text("❌ خطا در دریافت اطلاعات از سرور.")


@dp.message(F.text == "📈 دریافت چارت‌های زنده")
async def handle_charts_menu(message: Message):
    await message.answer("📈 لطفاً چارت مورد نظر خود را انتخاب کنید تا عکس آن برایتان ارسال شود:",
                         reply_markup=get_charts_keyboard())


@dp.message(F.text == "🧮 ماشین‌حساب خرید طلا")
async def handle_gold_help(message: Message):
    await message.answer(
        "⚖️ <b>ماشین‌حساب خرید طلا</b>\n\n"
        "برای محاسبه قیمت نهایی خرید طلا، وزن و درصد اجرت/سود را به این شکل بفرستید:\n\n"
        "مثال: <code>/gold 10 14</code>\n"
        "(یعنی ۱۰ گرم طلا با ۱۴ درصد اجرت و سود)"
    )


@dp.message(F.text == "🔄 تبدیل عیار آب‌شده (۷۳۰ به ۷۵۰)")
async def handle_abshodeh_help(message: Message):
    await message.answer(
        "🔄 <b>مبدل طلای آب‌شده (عیار ۷۳۰ به ۷۵۰)</b>\n\n"
        "برای تبدیل وزن طلای آب‌شده به عیار استاندارد ۱۸ عیار، وزن را به این شکل بفرستید:\n\n"
        "مثال: <code>/abshodeh 15.5</code>\n"
        "(یعنی ۱۵.۵ گرم طلای آب‌شده عیار ۷۳۰)"
    )


@dp.message(Command("repost"))
async def cmd_repost(message: Message):
    await update_channel_board(force_new=True)
    await message.answer("✅ تابلو جدید مجدداً در کانال ارسال و سنجاق شد!")


@dp.message(Command("gold"))
async def cmd_gold_calc(message: Message):
    """ماشین حساب طلا: /gold [وزن به گرم] [اجرت کل به درصد]"""
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ فرمت اشتباه! مثال صحیح:\n<code>/gold 10 14</code>")
        return

    try:
        weight = float(parts[1])
        fee_pct = float(parts[2]) if len(parts) > 2 else 16.0
    except ValueError:
        await message.answer("❌ لطفاً اعداد را به صورت انگلیسی وارد کنید (مثال: <code>/gold 10 14</code>).")
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
        f"• نرخ هر گرم طلای ۱۸ (عیار ۷۵۰): <code>{format_price(gold_18k)}</code> تومان\n"
        f"• ارزش طلای خام: <code>{format_price(raw_price)}</code> تومان\n"
        f"• اجرت، سود و مالیات ({fee_pct}%): <code>{format_price(final_price - raw_price)}</code> تومان\n\n"
        f"💰 <b>قیمت نهایی قابل پرداخت:</b> <code>{format_price(final_price)}</code> تومان"
    )


@dp.message(Command("abshodeh"))
async def cmd_abshodeh_calc(message: Message):
    """تبدیل طلای آب‌شده ۷۳۰ به ۷۵۰"""
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ فرمت اشتباه! مثال صحیح:\n<code>/abshodeh 10</code>")
        return

    try:
        weight_730 = float(parts[1])
    except ValueError:
        await message.answer("❌ لطفاً وزن را به صورت عدد انگلیسی وارد کنید (مثال: <code>/abshodeh 10</code>).")
        return

    data = await fetch_prices()
    if not data or not data.get("gold_18k"):
        await message.answer("❌ خطا در نرخ لحظه‌ای طلا.")
        return

    gold_18k = float(data["gold_18k"])
    equivalent_weight_750 = (weight_730 * 730) / 750
    total_price = equivalent_weight_750 * gold_18k

    await message.answer(
        f"🔄 <b>محاسبه و تبدیل عیار طلا:</b>\n\n"
        f"• وزن طلای آب‌شده (عیار ۷۳۰): <code>{weight_730}</code> گرم\n"
        f"• معادل وزن با عیار ۷۵۰ (۱۸ عیار): <code>{round(equivalent_weight_750, 3)}</code> گرم\n"
        f"• نرخ پایه عیار ۷۵۰: <code>{format_price(gold_18k)}</code> تومان\n\n"
        f"💰 <b>ارزش کل معامله:</b> <code>{format_price(total_price)}</code> تومان"
    )


@dp.callback_query(F.data.startswith("pv_chart_"))
async def cb_send_pv_chart(callback: CallbackQuery):
    chart_key = callback.data.replace("pv_", "")
    chart_info = CHARTS.get(chart_key)
    if not chart_info:
        return
    title, url = chart_info
    fresh_url = f"{url}?t={int(time.time())}"

    await callback.message.answer_photo(
        photo=fresh_url,
        caption=f"📊 <b>{title}</b>\n\n✅ نمودار لحظه‌ای درخواستی شما."
    )
    await callback.answer("نمودار ارسال شد ✅")


@dp.callback_query(F.data == "refresh_price")
async def cb_refresh_price(callback: CallbackQuery):
    data = await fetch_prices()
    if not data:
        await callback.answer("خطا در دریافت اطلاعات!", show_alert=True)
        return
    new_text = build_channel_message(data, channel_id=CHANNEL_ID)
    try:
        await callback.message.edit_text(new_text, reply_markup=get_channel_keyboard())
        await callback.answer("✅ قیمت‌ها بروزرسانی شد")
    except Exception:
        await callback.answer("قیمت‌ها تغییری نکرده است ✅")


@dp.inline_query()
async def inline_calculator(query: InlineQuery):
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
            title=f"💵 {amount:g} دلار = {format_price(usd_total)} تومان",
            description=f"نرخ واحد: {format_price(data.get('usd', 0))} تومان",
            input_message_content=InputTextMessageContent(
                message_text=f"💵 <b>{amount:g} دلار آمریکا:</b> <code>{format_price(usd_total)}</code> تومان\n📢 {CHANNEL_ID}"
            )
        ),
        InlineQueryResultArticle(
            id="gold_calc",
            title=f"✨ {amount:g} گرم طلا ۱۸ = {format_price(gold_total)} تومان",
            description=f"نرخ هر گرم: {format_price(data.get('gold_18k', 0))} تومان",
            input_message_content=InputTextMessageContent(
                message_text=f"✨ <b>{amount:g} گرم طلای ۱۸ عیار:</b> <code>{format_price(gold_total)}</code> تومان\n📢 {CHANNEL_ID}"
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