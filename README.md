# 💎 Mazzaneh (مظنه) | Real-Time Market & Gold Radar Bot

### ⚡ Automated Telegram Channel Manager, Gold Bubble Radar & Inline Currency Engine

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Aiogram](https://img.shields.io/badge/Aiogram_3.x-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![AsyncIO](https://img.shields.io/badge/AsyncIO-Event_Driven-00C7B7?style=for-the-badge&logo=fastapi&logoColor=white)
![AWS](https://img.shields.io/badge/AWS_EC2-Ready-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)

**Mazzaneh (مظنه)** is a blazing-fast, fully asynchronous Telegram bot and automated channel broadcaster built for the Iranian financial market. Powered by the [Nabz](https://github.com/itsyebekhe/nabz) data pipeline, it tracks live **IRR exchange rates**, **18K Gold**, **Global Ounce (XAU)**, and **Gold Coins** with zero manual intervention.

Instead of spamming channel subscribers with hundreds of notifications a day, **Mazzaneh** maintains a **Live Pinned Dashboard** in your Telegram channel—silently editing the pinned message every 3 minutes *only* when market rates fluctuate.

## 🌟 Why Mazzaneh Stands Out

* 📌 **Zero-Spam Live Pinned Board:** Automatically posts, pins, and updates a single master dashboard in your Telegram channel using `APScheduler` and smart diff-checking.
* 🔎 **Smart Gold Coin Bubble Radar:** Computes the real-time intrinsic value of the Emami Gold Coin against market prices, displaying the exact bubble in Tomans and a dynamic risk indicator (`🟢 Low` / `🟡 Moderate` / `🔴 High Risk`).
* 📈 **Interactive Visual Trend Charts:** On-demand inline buttons that deliver fresh, cache-busted visual charts for **USD**, **EUR**, **18K Gold**, and **Emami Coin**.
* ⚖️ **Jewelry Buyer's Calculator (`/gold`):** A practical retail calculator that computes the exact fair price of gold jewelry by factoring in weight (grams), craftsmanship fee (*Ojrat*), seller profit, and tax.
* ⚡ **Everywhere Inline Converter:** Type `@YourBotUsername [amount]` in *any* Telegram chat or group to convert USD, EUR, or Gold weight into Tomans on the fly.

## 📱 Live Channel & Bot Preview

```text
📊 تابلو زنده مظنه | نبض بازار
📅 ۱۷ آبان ۱۴۰۵

💵 ارزهای شاخص:
• دلار آزاد: 264,635 تومان
• یورو: 295,000 تومان
• پوند انگلیس: 349,900 تومان
• درهم امارات: 72,060 تومان
• لیر ترکیه: 5,360 تومان

✨ طلا و سکه:
• طلای ۱۸ عیار: 25,151,210 تومان
• مثقال طلا: 108,950,000 تومان
• انس جهانی طلا: 4068.76 دلار
• سکه امامی: 257,500,000 تومان
• سکه بهار آزادی: 248,000,000 تومان
• نیم‌سکه: 137,000,000 تومان
• ربع‌سکه: 72,500,000 تومان

🔎 رادار حباب سکه امامی:
• مقدار حباب: 5,214,800 تومان (🟢 %2.1)

🕒 بروزرسانی منبع: 12:22:30
📢 @Mazzaneh
```

## 🛠️ Tech Stack & Engineering Highlights

| Component | Technology | Role in Architecture |
| :--- | :--- | :--- |
| **Core Framework** | `aiogram 3.x` | Modern, fully asynchronous Telegram Bot API framework |
| **Network Layer** | `aiohttp` | Non-blocking HTTP client for high-speed JSON & chart fetching |
| **Task Scheduling** | `APScheduler` | Background `AsyncIOScheduler` for 3-minute channel syncs |
| **Security & Config** | `python-dotenv` | Strict separation of secrets (`.env`) from application logic |
| **Data Pipeline** | `Nabz JSON API` | Serverless-backed real-time market rates & visual charts |

## 🧮 Financial Engine: Gold Coin Bubble Formula

**Mazzaneh** calculates the real-time intrinsic bullion value of the Iranian Emami Gold Coin ($8.133\text{g}$ weight, $900$ fineness) using the standard market formula:

$$\text{Intrinsic Value} = \left( \frac{\text{Global Gold Ounce (USD)} \times \text{USD Rate (IRR)} \times 8.133}{31.1035} \right) \times 0.900$$

$$\text{Bubble Percentage} = \left( \frac{\text{Market Coin Price} - \text{Intrinsic Value}}{\text{Intrinsic Value}} \right) \times 100$$

## 📂 Project Structure

```text
Mazzaneh/
├── 📁 src/
│   ├── 📄 __init__.py      # Package initializer
│   ├── ⚙️ config.py        # Environment variable loader & validation
│   ├── 🌐 fetcher.py       # Async HTTP client (aiohttp) for market data
│   ├── 🎨 formatter.py     # Bubble radar math & HTML message templates
│   └── 🤖 bot.py           # Core aiogram handlers, inline engine & scheduler
├── 🔒 .env.example         # Safe environment template for developers
├── 🚫 .gitignore           # Prevents leaking .env and .venv to Git
├── 📦 requirements.txt     # Pinned production dependencies
└── 📖 README.md            # Project documentation
```

## 🚀 Quick Start Guide

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/S3nsi0ne/Mazzaneh.git
cd Mazzaneh
```

### 2️⃣ Set Up Virtual Environment & Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3️⃣ Configure Environment Variables

Copy the template file and add your secret keys:

```bash
cp .env.example .env
nano .env
```

```env
BOT_TOKEN=123456789:AAH_your_real_telegram_bot_token
CHANNEL_ID=@your_channel_username
NABZ_API_URL=https://raw.githubusercontent.com/itsyebekhe/nabz/main/market.json
```

*💡 **Tip:** Make sure your bot is added as an **Administrator** in your target channel with `Post Messages`, `Edit Messages`, and `Pin Messages` permissions. Also enable `/setinline` in [@BotFather](https://t.me/BotFather).*

### 4️⃣ Launch the Bot

```bash
PYTHONPATH=. python3 src/bot.py
```

## 🎮 Bot Commands & Interactive Features

| Trigger | Command / Syntax | Description |
| :--- | :--- | :--- |
| 🚀 **Welcome** | `/start` | Displays the interactive onboarding guide and available tools. |
| 📊 **Live Market** | `/price` | Sends the full market board with interactive chart & refresh buttons. |
| ⚖️ **Gold Calc** | `/gold [weight] [fee%]` | Example: `/gold 4.5 14` → Calculates final price for `4.5g` gold with `14%` fee. |
| ⚡ **Inline Mode** | `@BotUsername 250` | Type in any chat to instantly convert `250` USD, EUR, or Gold grams to Tomans. |

## ☁️ Production Deployment (AWS EC2 + `systemd`)

To keep **Mazzaneh** running 24/7 in the background on an Ubuntu server with automatic crash recovery:

1. **Create the service definition:**

```bash
sudo nano /etc/systemd/system/mazzaneh.service
```

2. **Paste the production configuration:**

```ini
[Unit]
Description=Mazzaneh Telegram Live Market Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Mazzaneh
Environment="PYTHONPATH=/home/ubuntu/Mazzaneh"
ExecStart=/home/ubuntu/Mazzaneh/.venv/bin/python src/bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

3. **Enable and start the daemon:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable mazzaneh
sudo systemctl start mazzaneh
sudo systemctl status mazzaneh
```

4. **View real-time logs:**

```bash
sudo journalctl -u mazzaneh -f
```

## 🗺️ Future Roadmap

* 🔔 **Personal Price Alerts:** Allow users to set custom USD/Gold target triggers in private chat.
* 💼 **Personal Portfolio Tracker:** Track daily profit/loss of personal currency and gold holdings.
* 🖼️ **Dynamic Pillow Image Cards:** Generate custom branded story graphics for Instagram & Telegram.

## 👨‍💻 Author & Acknowledgments

* **Developed by:** [S3nsi0ne](https://github.com/S3nsi0ne)
* **Data Pipeline:** Powered by [Nabz (itsyebekhe)](https://github.com/itsyebekhe/nabz)
* **License:** Distributed under the **MIT License**.