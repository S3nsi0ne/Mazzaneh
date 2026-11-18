import os
from dotenv import load_dotenv

# بارگذاری اطلاعات از فایل .env
load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


BOT_TOKEN = _require_env("BOT_TOKEN")
CHANNEL_ID = _require_env("CHANNEL_ID")
NABZ_API_URL = _require_env("NABZ_API_URL")

# یک تست کوچک برای اینکه مطمئن شویم توکن درست خوانده شده
if __name__ == "__main__":
    print("Token loaded:", bool(BOT_TOKEN))
    print("Channel ID:", CHANNEL_ID)