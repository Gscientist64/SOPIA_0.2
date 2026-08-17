# keep_alive.py
# Prevents Render free tier from sleeping after 15 minutes of inactivity.
#
# Render free tier spins down after ~15 min without traffic, then the first
# request after that takes ~30-60s to boot again. A periodic ping keeps the
# instance warm so responses are always instant.
#
# Option 1 (easiest, no code): UptimeRobot (free) — https://uptimerobot.com
#   Create a "HTTP(s)" monitor → URL: https://YOUR-APP.onrender.com/health
#   Interval: every 5 minutes → free tier is enough.
#
# Option 2 (this script): run it on ANY always-on machine (your PC, a free
#   GitHub Action cron, or a tiny cloud function). It just pings /health.

import time
import requests
import os

# Change this to your Render URL once deployed.
TARGET = os.getenv("TARGET_URL", "http://localhost:5050/health")
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", "300"))  # every 5 min
MAX_RETRIES = 3


def ping_once() -> bool:
    """Ping the health endpoint once. Returns True on success."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(TARGET, timeout=20)
            if resp.status_code == 200:
                print(f"✅ [{time.strftime('%H:%M:%S')}] Ping OK ({resp.status_code})")
                return True
            print(f"⚠️  [{time.strftime('%H:%M:%S')}] Status {resp.status_code} (attempt {attempt})")
        except Exception as e:
            print(f"❌ [{time.strftime('%H:%M:%S')}] Error: {e} (attempt {attempt})")
        time.sleep(10)
    return False


def main():
    print(f"🔄 Keep-alive started → {TARGET} every {INTERVAL_SECONDS}s")
    print("   Press Ctrl+C to stop.")
    while True:
        ping_once()
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
