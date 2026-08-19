<div align="center">

# 🏥 SOPiA

### Standard Operating Procedure Intelligent Assistance

**SOPiA** (Standard Operating Procedure Intelligent Assistance) is a conversational AI that brings
advanced HIV/AIDS care protocols to healthcare workers — instantly, on any device.

[Features](#-features) · [Demo](#-demo) · [Architecture](#-architecture) · [Quick Start](#-quick-start) · [Deploy](#-deployment) · [Tech Stack](#-tech-stack)

</div>

---

## ✨ Features

- **💬 Intelligent Q&A** — Ask natural-language questions about HIV care protocols and get accurate, sourced answers
- **🏥 Medical Knowledge Base** — Structured extraction of clinical concepts:
  - Advanced HIV Disease (AHD) definitions & criteria
  - CD4+ cell count monitoring thresholds
  - WHO clinical staging
  - TB screening protocols
  - ARV medication regimens (TDF, 3TC, DTG, etc.)
- **🧠 Clinical Reasoning Engine** — Rule-based evaluation of patient scenarios with treatment recommendations
- **🔬 Confidence Scoring** — Knows what it doesn't know; flags low-confidence answers for verification
- **📚 Source Attribution** — Every answer cites the SOP documents it came from
- **➕ Add SOPs without retraining** — Upload new protocols via REST API
- **📱 Multi-channel** — Web chat UI + Telegram bot (free) + WhatsApp-ready (via Twilio)

---

## 🌐 Demo

Deployed MVP: **`https://sopia-mvp.onrender.com`**

Try it live:
- `/` — main chat interface (pink theme)
- `/demo` — same chat UI (alias)
- `/health` — service health check

---

## 🏗 Architecture

```
┌──────────────┐     ┌───────────────┐     ┌──────────────────┐     ┌─────────────┐
│  Web UI      │ ──► │  Flask API    │ ──► │  Chat Engine     │ ──► │  Google     │
│  Telegram    │     │  (app.py)     │     │  (retrieval +    │     │  Gemini LLM │
│  WhatsApp*   │     │               │     │   reasoning)     │     │             │
└──────────────┘     └───────┬───────┘     └────────┬─────────┘     └─────────────┘
                             │                      │
                             ▼                      ▼
                    ┌──────────────────┐   ┌──────────────────┐
                    │  SOP Knowledge   │   │  Medical KB      │
                    │  Base (pickle)   │   │  + Clinical      │
                    │  sopia_kb.pkl    │   │  Reasoning Rules │
                    └──────────────────┘   └──────────────────┘
```

**Flow:** User question → semantic search over SOP chunks → context stitching →
LLM response generation → formatted answer with confidence & sources.

---

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.10+
- A [Google AI](https://aistudio.google.com/) API key (or OpenAI key)

### 1. Clone & install
```bash
git clone https://github.com/Gscientist64/SOPIA_0.2.git
cd SOPIA_0.2
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

### 2. Configure environment
```bash
copy .env.example .env         # Windows
# edit .env and set GOOGLE_API_KEY
```

### 3. Build the knowledge base (one time)
```bash
python build_final_kb.py
# Generates sopia_kb.pkl from your SOP documents
```

### 4. Run
```bash
python app.py
# → http://localhost:5050
```

---

## 📚 Adding SOP Content

**Via API** (no retraining):
```bash
curl -X POST http://localhost:5050/add-sop-text \
  -H "Content-Type: application/json" \
  -d '{"source_id":"my_protocol","text":"..."}'
```

**From file**:
```bash
python add_sop_from_file.py
```

**Rebuild everything**:
```bash
python build_final_kb.py
```

---

## 🌍 Deployment (Render — Free Tier)

The project is pre-configured for [Render](https://render.com) free tier (24/7 uptime, $0).

1. Push this repo to GitHub
2. At [render.com](https://render.com): **New +** → **Web Service** → connect your repo
3. Use these settings (also in `render.yaml`):
   - **Build:** `pip install -r requirements-render.txt`
   - **Start:** `gunicorn --workers 1 --timeout 120 --bind 0.0.0.0:$PORT app:app`
4. Add environment variables:
   | Key | Value |
   |-----|-------|
   | `GOOGLE_API_KEY` | your key |
   | `DEBUG` | `False` |
   | `FLASK_ENV` | `production` |
5. **Keep it awake** (free tier sleeps after 15 min idle): add a free [UptimeRobot](https://uptimerobot.com) monitor pinging `/health` every 5 min.

> Full walkthrough → **[`MVP_DEPLOYMENT.md`](MVP_DEPLOYMENT.md)**

---

## 🤖 Telegram Bot (Free Messaging)

```bash
# 1. Get a token from @BotFather on Telegram
# 2. Add to .env:  TELEGRAM_BOT_TOKEN=...
python telegram_bot.py
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat` | Ask a question `{"question": "..."}` |
| `GET` | `/health` | Service health & status |
| `POST` | `/add-sop-text` | Add SOP content |
| `POST` | `/clinical-assessment` | Clinical scenario evaluation |
| `GET` | `/medical-concepts` | Browse extracted medical concepts |
| `GET` | `/treatment-pathways` | Browse clinical pathways |
| `GET` | `/topics` | Available topics |
| `GET` | `/suggestions` | Suggested questions |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python · Flask · Flask-CORS |
| LLM | Google Gemini (multi-key fallback) · OpenAI (optional) |
| Knowledge Base | Custom retrieval over prebuilt pickle (embeddings-ready) |
| Document Processing | python-docx · regex-based medical concept extraction |
| Messaging | Telegram (free) · Twilio (WhatsApp, ready) |
| Hosting | Render (free tier) · gunicorn |

---

## 📁 Project Structure

```
SOPIA_0.2/
├── app.py                  # Flask app, routes, medical KB, reasoning engine
├── build_final_kb.py       # Build the knowledge base pickle
├── chat_engine.py          # Q&A engine (retrieval + prompt + confidence)
├── document_processor.py   # DOCX → chunks + medical concept extraction
├── knowledge_base.py       # Knowledge base & caching
├── llm_client.py           # Gemini / OpenAI clients
├── telegram_bot.py         # Free Telegram channel
├── keep_alive.py           # Keep Render free tier awake
├── requirements.txt        # Local dev dependencies
├── requirements-render.txt # Lean deps for Render (no torch)
├── render.yaml             # Render Blueprint config
├── templates/
│   ├── chat_demo.html      # Main chat UI (pink theme, served at /)
│   ├── index.html          # Legacy full-featured chat UI
│   └── test.html
└── sops/ · data/ · new_sops/
```

---

## 🔒 Security

- `.env` is **git-ignored** — never commit secrets
- API keys are managed via environment variables (Render dashboard)
- Multi-key rotation + graceful offline fallback if an API fails
- Confidence scoring to flag uncertain medical answers

> ⚠️ **Medical disclaimer:** SOPiA is a decision-support tool, not a replacement for
> clinical judgment. Always verify critical guidance with a licensed professional.

---

## 🗺 Roadmap

- [x] Web chat interface
- [x] Medical concept extraction & clinical reasoning
- [x] Render free-tier deployment
- [ ] WhatsApp integration (Twilio) post-funding
- [ ] User authentication & conversation history
- [ ] Multi-language support
- [ ] Real embedding-based semantic search (sentence-transformers)

---

## 📄 License

Private / All rights reserved.

---

<div align="center">
  Made with ❤️ for healthcare workers in the field.
</div>
