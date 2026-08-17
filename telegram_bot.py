# telegram_bot.py — Free MVP messaging channel for SOPiA
#
# Telegram bots are 100% free, unlimited users, and work worldwide with no
# app download (web version available). Perfect for your MVP before you add
# paid Twilio WhatsApp.
#
# SETUP (5 minutes):
# 1. Open Telegram → message @BotFather → /newbot → follow prompts
#    → you get a token like: 123456789:ABCdefGhIJK...
# 2. Add the token to your .env:  TELEGRAM_BOT_TOKEN=123456789:ABC...
# 3. Run:  python telegram_bot.py
#    (Run it locally, or on any always-on machine / free hosting)
# 4. Users just open your bot link (BotFather gives you one) and type away.
#
# Uses long-polling (no webhooks), so it works without a public URL.

import os
import logging
import requests

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger("SOPiA-Telegram")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
API = f"https://api.telegram.org/bot{TOKEN}"
# Point this at your Render app once deployed, or localhost while developing.
SOPIA_API = os.getenv("SOPIA_API_URL", "http://localhost:5050/chat")


def get_updates(offset=None):
    """Fetch new messages from Telegram."""
    params = {"timeout": 25}
    if offset:
        params["offset"] = offset
    resp = requests.get(f"{API}/getUpdates", params=params, timeout=30)
    return resp.json().get("result", [])


def send_message(chat_id, text):
    """Send a text message to a Telegram chat."""
    data = {"chat_id": chat_id, "text": text, "disable_web_page_preview": True}
    requests.post(f"{API}/sendMessage", json=data)


def ask_sopia(question: str) -> str:
    """Forward the question to the SOPiA backend and return the answer."""
    try:
        resp = requests.post(SOPIA_API, json={"question": question}, timeout=90)
        resp.raise_for_status()
        data = resp.json()
        answer = data.get("answer", "No response.")
        # Truncate to Telegram's 4096-char limit
        if len(answer) > 4096:
            answer = answer[:4076] + "\n\n…[truncated]"
        return answer
    except Exception as e:
        log.error(f"Failed to reach SOPiA backend: {e}")
        return "⚠️ Sorry, I couldn't reach the knowledge engine right now. Please try again later."


def main():
    if not TOKEN:
        log.error("❌ TELEGRAM_BOT_TOKEN not set in .env — see instructions at top of this file.")
        return

    log.info("🤖 SOPiA Telegram bot starting (long-polling)…")
    offset = None
    while True:
        try:
            for update in get_updates(offset):
                offset = update["update_id"] + 1

                msg = update.get("message")
                if not msg or "text" not in msg:
                    continue

                chat_id = msg["chat"]["id"]
                question = msg["text"].strip()

                # Ignore commands like /start for now (could greet later)
                if question.startswith("/"):
                    if question == "/start":
                        send_message(chat_id, "👋 Welcome to SOPiA!\n\nAsk me anything about HIV care protocols, e.g.\n• What is AHD?\n• What are CD4 criteria?\n• First-line ART regimen?")
                    continue

                log.info(f"📨 [{chat_id}] {question[:80]}")
                send_message(chat_id, "⏳ Thinking…")
                answer = ask_sopia(question)
                send_message(chat_id, answer)
                log.info("✅ Reply sent.")
        except Exception as e:
            log.error(f"Loop error: {e}")
            time.sleep(3)


if __name__ == "__main__":
    import time
    main()
