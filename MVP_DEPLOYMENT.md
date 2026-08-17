# 🚀 SOPiA MVP — Deploy to Render (Free, 24/7 Uptime)

You decided: **Render, not ngrok** — so investors can visit even when your PC is off.
This turns the demo into a real **MVP** running 24/7 on Render's **free tier**.

## What You Get

| | Before (ngrok demo) | Now (Render MVP) |
|---|---|---|
| Availability | Only when PC is on | **24/7 (750 hrs/mo free)** |
| URL | Random per session | **Permanent** `https://sopia-mvp.onrender.com` |
| Cost | $0 | **$0** (free tier) |
| Chat interface | `/demo` | `/` + `/demo` |
| Messaging | None | **Telegram bot (free)** |
| Keep-awake | N/A | UptimeRobot or `keep_alive.py` |

**Total monthly cost: $20 (Google Pro only).**

---

## What Changed in Your Code (already done ✅)

1. **`app.py`** — reads `PORT` and `DEBUG` from env (Render injects `PORT` automatically).
2. **`requirements-render.txt`** (new) — lean deps: avoids the huge `torch` build that
   times out on Render free tier. The app loads the prebuilt `sopia_kb.pkl` directly,
   so heavy ML libs aren't needed at runtime.
3. **`render.yaml`** (updated) — free tier, health check, correct start command.
4. **`.gitignore`** (fixed) — `sopia_kb.pkl` is **now committed** so Render can load the KB.
5. **`keep_alive.py`** (new) — pings `/health` so the free tier doesn't sleep.
6. **`telegram_bot.py`** (new) — free Telegram channel for your MVP.

---

## Deploy in 6 Steps (~30 min)

### Step 1 — Push code to GitHub

Create a **private** repo on GitHub (secrets are in `.env`, so keep it private).

```bash
cd c:\SOPIA_0.2
git init
git add .
git commit -m "SOPiA MVP - Render deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/sopia.git
git push -u origin main
```

⚠️ **Double-check `sopia_kb.pkl` is tracked:**
```bash
git ls-files | findstr sopia_kb
# MUST show: sopia_kb.pkl
```
If it doesn't show, run `git add -f sopia_kb.pkl` and commit again.

### Step 2 — Create a Render account

1. Go to [render.com](https://render.com) → **Sign Up** → "Continue with GitHub".
2. Authorize Render to access your `sopia` repo.

### Step 3 — Create the Web Service

1. Click **New +** → **Web Service**.
2. Connect your `sopia` repository.
3. Render auto-detects `render.yaml` → click **Apply Blueprint**.
   (Or pick "Web Service" and copy settings below manually.)

**Manual settings (if not using blueprint):**
- **Name:** `sopia-mvp`
- **Runtime:** Python 3
- **Build Command:** `pip install -r requirements-render.txt`
- **Start Command:** `gunicorn --workers 1 --timeout 120 --bind 0.0.0.0:$PORT app:app`
- **Instance Type:** Free

### Step 4 — Add environment variables

In Render dashboard → your service → **Environment** → add:

| Key | Value |
|-----|-------|
| `GOOGLE_API_KEY` | `AQ.Ab8R...` (your Google Pro key) |
| `DEBUG` | `False` |
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | (generate: `python -c "import secrets; print(secrets.token_hex(32))"`) |

Optional (leave empty if unused): `OPENAI_API_KEY`, `TWILIO_*`.

⚠️ **Never commit `.env`** — Render dashboard is where secrets live.

### Step 5 — Deploy

1. Click **Create Web Service**.
2. Wait 2–4 min for the first build (it's fast because deps are lean).
3. When it says **Live**, visit:
   - `https://sopia-mvp.onrender.com/health` → should return JSON with `"ok": true`
   - `https://sopia-mvp.onrender.com/` → the chat interface
   - `https://sopia-mvp.onrender.com/demo` → the sleek demo UI

### Step 6 — Keep it awake (free)

Render free tier sleeps after ~15 min of no traffic; first request after sleep takes ~30s.

**Option A — UptimeRobot (free, zero code):**
1. Go to [uptimerobot.com](https://uptimerobot.com) → Sign up (free).
2. Add monitor → **HTTP(s)** → URL: `https://sopia-mvp.onrender.com/health`
3. Interval: **5 minutes** → saves 1/3 of your 750 free hours!
   (At 5-min pings you use ~216 hrs/mo — well under 750.)

**Option B — `keep_alive.py`:** run on any always-on machine:
```bash
python keep_alive.py
# set env: TARGET_URL=https://sopia-mvp.onrender.com/health
```

---

## Add the Free Telegram Bot (optional but great for MVP)

Gives users a real chat channel beyond the web — 100% free, unlimited users.

1. Open Telegram → message **@BotFather** → `/newbot` → follow prompts.
2. Copy the token it gives you.
3. Add to your `.env`: `TELEGRAM_BOT_TOKEN=123456789:ABC...`
4. Set `SOPIA_API_URL=https://sopia-mvp.onrender.com/chat`
5. Run: `python telegram_bot.py`
6. Share the bot link with test users.

> For a "set-and-forget" bot, host `telegram_bot.py` on a free always-on service
> (e.g., a free GitHub Actions cron or a free-tier cloud function) later. For now,
> running it on your PC during presentations is fine.

---

## Verifying It All Works

```bash
# 1. Health check (should be instant JSON)
curl https://sopia-mvp.onrender.com/health

# 2. Ask a question
curl -X POST https://sopia-mvp.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"What is AHD?"}'

# 3. From any phone/tablet (no PC needed!)
#    Open https://sopia-mvp.onrender.com in the browser
```

**Test with your PC OFF** — that's the whole point. The site keeps running. ✅

---

## Free Tier Limits (know these)

| Limit | Free Tier | Our MVP usage |
|-------|-----------|---------------|
| Runtime | 750 hrs/month | ~216-720 hrs (fine) |
| RAM | 512 MB | OK — no torch at runtime |
| Build | ~5 min, 1 GB disk | OK — lean deps |
| Sleep | after 15 min idle | Solved with UptimeRobot |
| Bandwidth | 100 GB/month | Plenty for MVP |

If you ever exceed free limits, the **Starter plan ($7/mo)** removes sleep and
boosts resources — still cheap.

---

## What NOT To Do (gotchas)

- ❌ Don't add `torch`/`sentence-transformers` to Render build — huge, slow, often fails.
  Rebuild the KB **locally** with `python build_final_kb.py`, then commit the new `sopia_kb.pkl`.
- ❌ Don't commit `.env` (Render dashboard holds secrets).
- ❌ Don't use `app.run(port=5050)` hardcoded (already fixed to use `$PORT`).
- ❌ Don't run multiple gunicorn workers on free tier (1 worker is correct for 512MB).

---

## Updating the Knowledge Base Later

1. On your PC: `python build_final_kb.py` (regenerates `sopia_kb.pkl`).
2. Commit & push: Render auto-redeploys (autoDeploy: true).
3. New SOPs go live — no rebuild needed on the server.

---

## Cost Summary (MVP)

| Item | Monthly |
|------|---------|
| Google Pro API | $20 |
| Render (free tier) | $0 |
| UptimeRobot | $0 |
| Telegram bot | $0 |
| **Total** | **$20** |

---

## After You Get Funding

- Upgrade Render to **Starter ($7/mo)** → no sleep, more RAM.
- Add **Twilio WhatsApp** (see `INTEGRATION_WHATSAPP.md`).
- Add a real database (Firebase free → MongoDB paid) if you track users.
- Scale gunicorn workers as traffic grows.

**You now have a 24/7 live product for $20/month. Go get that funding! 🎉**
