# telegram_bot.py — SOPiA Telegram Bot (standalone version)
#
# Telegram bots are 100% free, unlimited users, and work worldwide with no
# app download. This is your free messaging channel before paid WhatsApp.
#
# QUICK SETUP (5 minutes):
# 1. In Telegram, message @BotFather → /newbot → follow prompts
#    → you get a token like: 123456789:ABCdefGhIJK...
# 2. Add it to your .env:  TELEGRAM_BOT_TOKEN=123456789:ABC...
#    And set:              SOPIA_API_URL=https://sopia-mvp.onrender.com/chat
# 3. Run:  python telegram_bot.py
#    (Locally while testing, or it can be embedded in app.py for 24/7 hosting)
# 4. Share your bot's link (BotFather gives you one) with users.
#
# Uses long-polling (no webhook / no public URL needed).

import os
import time
import logging
import requests

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger("SOPiA-Telegram")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
API = f"https://api.telegram.org/bot{TOKEN}"
SOPIA_API = os.getenv("SOPIA_API_URL", "http://localhost:5050/chat")

WELCOME = (
    "👋 Welcome to SOPiA!\n\n"
    "I'm an AI assistant for HIV care protocols. Ask me anything, e.g.:\n"
    "• What is AHD?\n"
    "• What are CD4 count criteria?\n"
    "• What is the first-line ART regimen?\n"
    "• When should ART start?\n\n"
    "Type /help for more info."
)
HELP = (
    "🤖 SOPiA — AI HIV Care Assistant\n\n"
    "Just type your medical question and I'll answer using the SOP knowledge base.\n\n"
    "Commands:\n"
    "• /start — welcome message\n"
    "• /help — this help\n"
    "• /clear — reset conversation\n\n"
    "⚠️ Decision support only — always verify with a licensed clinician."
)


def call(method: str, **params):
    """Helper for Telegram Bot API calls."""
    try:
        resp = requests.post(f"{API}/{method}", json=params, timeout=30)
        resp.raise_for_status()
        return resp.json().get("result")
    except Exception as e:
        log.error(f"Telegram API {method} failed: {e}")
        return None


def get_updates(offset=None):
    resp = requests.get(f"{API}/getUpdates", params={"timeout": 25, "offset": offset}, timeout=30)
    return resp.json().get("result", [])


def send_message(chat_id, text, reply_to=None):
    """Send a text message.

    Medical answers often contain raw HTML-sensitive characters like "<"
    (e.g. "CD4 < 200"). We send as PLAIN TEXT to avoid Telegram's HTML
    parser rejecting the message with a 400 error. If parse_mode is ever
    requested and it fails, we fall back to plain text automatically.
    """
    data = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True,
    }
    if reply_to:
        data["reply_to_message_id"] = reply_to
    try:
        resp = requests.post(f"{API}/sendMessage", json=data, timeout=30)
        # If we ever add parse_mode later, retry without it on a 400.
        if resp.status_code == 400 and "parse_mode" in data:
            data.pop("parse_mode")
            resp = requests.post(f"{API}/sendMessage", json=data, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        log.error(f"Telegram API sendMessage failed: {e}")
        return None


def show_typing(chat_id):
    call("sendChatAction", chat_id=chat_id, action="typing")


def ask_sopia(question: str) -> str:
    """Forward the question to the SOPiA backend and return a formatted answer."""
    try:
        resp = requests.post(SOPIA_API, json={"question": question}, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        answer = (data.get("answer") or "No response.").strip()
        # Telegram hard limit is 4096 chars per message — truncate if needed
        if len(answer) > 4096:
            answer = answer[:4076] + "\n\n…[truncated]"
        return answer
    except Exception as e:
        log.error(f"Failed to reach SOPiA backend: {e}")
        return "⚠️ Sorry, I couldn't reach the knowledge engine right now. Please try again later."


def handle_message(chat_id, text, message_id=None):
    text = (text or "").strip()
    if not text:
        return

    # Commands
    if text.startswith("/"):
        cmd = text.split()[0].lower()
        if cmd in ("/start", "/help"):
            send_message(chat_id, WELCOME if cmd == "/start" else HELP)
        elif cmd == "/clear":
            send_message(chat_id, "🧹 Conversation reset. Ask away!")
        else:
            send_message(chat_id, "Unknown command. Try /help.")
        return

    # Normal question
    log.info(f"📨 [{chat_id}] {text[:80]}")
    show_typing(chat_id)
    answer = ask_sopia(text)
    send_message(chat_id, answer, reply_to=message_id)
    log.info("✅ Reply sent.")


def main():
    if not TOKEN:
        log.error("❌ TELEGRAM_BOT_TOKEN not set in .env — see instructions at top of this file.")
        return

    log.info(f"🤖 SOPiA Telegram bot starting (long-polling)… → {SOPIA_API}")
    offset = None
    while True:
        try:
            for update in get_updates(offset):
                offset = update["update_id"] + 1
                msg = update.get("message")
                if not msg or "text" not in msg:
                    continue
                handle_message(
                    msg["chat"]["id"],
                    msg["text"],
                    msg.get("message_id"),
                )
        except requests.exceptions.Timeout:
            pass  # normal — long poll timed out, keep looping
        except Exception as e:
            log.error(f"Loop error: {e}")
            time.sleep(3)


if __name__ == "__main__":
    main()
