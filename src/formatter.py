import asyncio
from src.fetcher import fetch_prices


def calculate_coin_bubble(coin_price: float, usd_price: float, gold_ounce: float) -> tuple[int, float]:
    """
    محاسبه ارزش ذاتی و درصد حباب سکه امامی
    فرمول استاندارد بازار: ((انس جهانی * قیمت دلار * 8.133) / 31.1035) * 0.900
    """
    if not all([coin_price, usd_price, gold_ounce]) or usd_price == 0 or gold_ounce == 0:
        return 0, 0.0

    intrinsic_value = ((gold_ounce * usd_price * 8.133) / 31.1035) * 0.900
    bubble_amount = int(coin_price - intrinsic_value)
    bubble_percent = (bubble_amount / intrinsic_value) * 100
    return bubble_amount, round(bubble_percent, 1)


def format_price(value: int | float | str) -> str:
    """جداسازی سه رقم سه رقم اعداد"""
    try:
        return f"{int(float(value)):,}"
    except (ValueError, TypeError):
        return "نامشخص"


def build_channel_message(data: dict, channel_id: str = "@Mazzaneh") -> str:
    """ساخت متن نهایی برای ارسال یا ویرایش در کانال مظنه"""
    usd = data.get("usd", 0)
    eur = data.get("eur", 0)
    gbp = data.get("gbp", 0)
    aed = data.get("aed", 0)
    try_rate = data.get("try", 0)

    gold_18k = data.get("gold_18k", 0)
    gold_mesghal = data.get("gold_mesghal", 0)
    ounce = data.get("gold_ounce", 0)

    coin_emami = data.get("coin_emami", 0)
    coin_bahar = data.get("coin_bahar", 0)
    coin_half = data.get("coin_half", 0)
    coin_quarter = data.get("coin_quarter", 0)

    date_shamsi = data.get("date_shamsi_full", data.get("date_shamsi", ""))
    updated_time = data.get("updated_at", "").split(" ")[-1] if data.get("updated_at") else ""

    # محاسبه حباب سکه امامی
    bubble_tomans, bubble_pct = calculate_coin_bubble(
        float(coin_emami), float(usd), float(ounce)
    )
    bubble_sign = "🔴" if bubble_pct > 18 else "🟡" if bubble_pct > 10 else "🟢"

    text = (
        f"📊 <b>تابلو زنده مظنه | نبض بازار</b>\n"
        f"📅 {date_shamsi}\n\n"
        f"💵 <b>ارزهای شاخص:</b>\n"
        f"• دلار آزاد: <code>{format_price(usd)}</code> تومان\n"
        f"• یورو: <code>{format_price(eur)}</code> تومان\n"
        f"• پوند انگلیس: <code>{format_price(gbp)}</code> تومان\n"
        f"• درهم امارات: <code>{format_price(aed)}</code> تومان\n"
        f"• لیر ترکیه: <code>{format_price(try_rate)}</code> تومان\n\n"
        f"✨ <b>طلا و سکه:</b>\n"
        f"• طلای ۱۸ عیار: <code>{format_price(gold_18k)}</code> تومان\n"
        f"• مثقال طلا: <code>{format_price(gold_mesghal)}</code> تومان\n"
        f"• انس جهانی طلا: <code>{ounce}</code> دلار\n"
        f"• سکه امامی: <code>{format_price(coin_emami)}</code> تومان\n"
        f"• سکه بهار آزادی: <code>{format_price(coin_bahar)}</code> تومان\n"
        f"• نیم‌سکه: <code>{format_price(coin_half)}</code> تومان\n"
        f"• ربع‌سکه: <code>{format_price(coin_quarter)}</code> تومان\n\n"
        f"🔎 <b>رادار حباب سکه امامی:</b>\n"
        f"• مقدار حباب: <code>{format_price(bubble_tomans)}</code> تومان ({bubble_sign} %{bubble_pct})\n\n"
        f"🕒 <i>بروزرسانی منبع: {updated_time}</i>\n"
        f"📢 {channel_id}"
    )
    return text


# تست خروجی متن قبل از ارسال به تلگرام
if __name__ == "__main__":
    async def test_format():
        data = await fetch_prices()
        if data:
            print(build_channel_message(data))


    asyncio.run(test_format())