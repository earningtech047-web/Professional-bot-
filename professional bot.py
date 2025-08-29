# professional_bot.py
# Pydroid friendly long-polling Telegram bot
# Requirements: requests
# Run: pip install requests
# Then: python3 professional_bot.py

import os
import time
import requests
import sys
from datetime import datetime

# ---------- CONFIG ----------
# OPTION A: Direct (you provided token) - paste token here:
BOT_TOKEN = "8264548134:AAHfk21dnlr8M3M1Bz4fgHttXFz_2ZPNxWY"

# OPTION B (safer): uncomment these lines and comment OPTION A above,
# then set environment variable BOT_TOKEN before running:
# BOT_TOKEN = os.environ.get("BOT_TOKEN")
# if not BOT_TOKEN:
#     sys.exit("Set BOT_TOKEN env var or paste token in code.")

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
POLL_TIMEOUT = 30
SLEEP_ON_ERROR = 5

# Professional-looking header / footer used in messages
BOT_NAME = "SmartPro Bot"
HEADER = "🔷 <b>SmartPro</b> — Professional Services"
FOOTER = "\n\n© SmartPro • For queries use /help"

# Reply keyboard (6 buttons) — 2 rows × 3 columns
MAIN_KEYBOARD = {
    "keyboard": [
        [{"text": "ℹ️ About"}, {"text": "🧾 Services"}, {"text": "💼 Pricing"}],
        [{"text": "💸 Invest"}, {"text": "📞 Contact"}, {"text": "❓ Help"}]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}

# Inline keyboard (example) — if you want buttons that open links:
MAIN_INLINE = {
    "inline_keyboard": [
        [
            {"text": "Website", "url": "https://example.com"},
            {"text": "Telegram Channel", "url": "https://t.me/yourchannel"}
        ]
    ]
}

# ---------- Helper functions ----------
def log(msg):
    print(f"[{datetime.now().isoformat(sep=' ', timespec='seconds')}] {msg}", flush=True)

def send_message(chat_id, text, reply_markup=None, parse_mode="HTML"):
    data = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    if reply_markup:
        data["reply_markup"] = reply_markup
    try:
        resp = requests.post(API_URL + "/sendMessage", json=data, timeout=10)
        if resp.status_code != 200:
            log(f"send_message failed {resp.status_code} {resp.text}")
        return resp.json()
    except Exception as e:
        log(f"send_message exception: {e}")
        return None

def answer_start(chat_id, first_name=None):
    name = first_name or ""
    text = (
        f"{HEADER}\n\n"
        f"Hi <b>{name}</b> — Welcome! This bot demonstrates a professional menu with quick buttons.\n\n"
        "Use the buttons below to explore our options."
        f"{FOOTER}"
    )
    send_message(chat_id, text, reply_markup=MAIN_KEYBOARD)

# ---------- Handlers for each button ----------
def handle_text(chat_id, text, first_name=None):
    text = (text or "").strip()

    if text == "/start":
        answer_start(chat_id, first_name)
        return

    if text == "/menu":
        send_message(chat_id, "<b>Main Menu</b>\nChoose an option:", reply_markup=MAIN_KEYBOARD)
        return

    # Buttons
    if text == "ℹ️ About":
        send_message(chat_id,
            "<b>About SmartPro</b>\n\nSmartPro provides premium investment & advisory solutions. "
            "Built for professionals who want reliable returns and best-in-class support." + FOOTER)
        return

    if text == "🧾 Services":
        send_message(chat_id,
            "<b>Our Services</b>\n\n• Investment advisory\n• Portfolio management\n• Wealth planning\n\n"
            "Reply with which service you want to know more about.")
        return

    if text == "💼 Pricing":
        send_message(chat_id,
            "<b>Pricing</b>\n\nStarter: ₹500/month — Basic signals\nPro: ₹2,000/month — Full portfolio support\n\n"
            "DM for corporate pricing.")
        return

    if text == "💸 Invest":
        send_message(chat_id,
            "<b>Invest with SmartPro</b>\n\nMinimum ₹500. We offer automated plans and personal manager support.\n"
            "To start, reply: <code>Start Invest</code> or visit our website." + FOOTER)
        return

    if text == "📞 Contact":
        send_message(chat_id,
            "<b>Contact Us</b>\n\nEmail: support@example.com\nPhone: +91-98765-43210\nTelegram: @SmartProSupport")
        return

    if text == "❓ Help":
        send_message(chat_id,
            "<b>Help</b>\n\nCommands:\n/start - Show welcome & menu\n/menu - Show menu again\n\n"
            "If you need human support, type: <code>Contact Agent</code>.")
        return

    # fallback: echo with professional tone
    send_message(chat_id,
        f"<b>Received</b>\n\nYou wrote:\n<code>{text}</code>\n\nIf you want the menu again, type /menu")

# ---------- Long-polling loop ----------
def get_updates(offset=None, timeout=POLL_TIMEOUT):
    params = {"timeout": timeout, "allowed_updates": ["message"]}
    if offset:
        params["offset"] = offset
    try:
        r = requests.get(API_URL + "/getUpdates", params=params, timeout=timeout + 5)
        return r.json()
    except Exception as e:
        log(f"get_updates exception: {e}")
        return None

def main_loop():
    log("Bot started (long-polling). Press Ctrl+C to stop.")
    offset = None
    while True:
        try:
            data = get_updates(offset)
            if not data:
                log("get_updates returned None, sleeping...")
                time.sleep(SLEEP_ON_ERROR)
                continue
            if not data.get("ok"):
                log(f"get_updates error: {data}")
                time.sleep(SLEEP_ON_ERROR)
                continue

            for update in data.get("result", []):
                offset = update["update_id"] + 1
                if "message" in update:
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    first_name = msg["from"].get("first_name")
                    text = msg.get("text", "")
                    log(f"Message from {first_name} ({chat_id}): {text}")
                    try:
                        handle_text(chat_id, text, first_name)
                    except Exception as e:
                        log(f"handler exception: {e}")
                        send_message(chat_id, "Sorry, an error occurred while processing your request.")
        except KeyboardInterrupt:
            log("KeyboardInterrupt - exiting.")
            break
        except Exception as e:
            log(f"Main loop exception: {e}")
            time.sleep(SLEEP_ON_ERROR)

if __name__ == "__main__":
    main_loop()
