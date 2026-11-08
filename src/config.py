import os
from dotenv import load_dotenv

# بارگذاری اطلاعات از فایل .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
NABZ_API_URL = os.getenv("NABZ_API_URL")

# یک تست کوچک برای اینکه مطمئن شویم توکن درست خوانده شده
if __name__ == "__main__":
    print("Token loaded:", bool(BOT_TOKEN))
    print("Channel ID:", CHANNEL_ID)