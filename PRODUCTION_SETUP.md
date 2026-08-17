# SOPiA Production Deployment Guide

## Phase 1: Get Google Pro API Key ✅

### Steps:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account that has the Pro subscription
3. Create a new project (or use existing):
   - Click "Select a Project" → "New Project"
   - Name it: `SOPIA_Production`
4. Enable Gemini API:
   - Go to APIs & Services → Enable APIs
   - Search for "Generative AI API"
   - Click "Enable"
5. Create API Key:
   - Go to Credentials → "Create Credentials" → "API Key"
   - Copy the key (it will be used in .env)
6. Set up billing:
   - Go to Billing → Link your Google Pro subscription
   - Your API key will now use paid tier

**Your API Key Format:** `AIza...` (similar to what you see in .env)

---

## Phase 2: Setup Twilio WhatsApp Business ✅

### Prerequisites:
- Twilio Account (you have: SID, Auth Token in .env)
- WhatsApp Business Account
- Business phone number

### Steps:

1. **Get Twilio WhatsApp Number:**
   - Log in to [Twilio Console](https://www.twilio.com/console)
   - Go to Messaging → Try it Out → Send an SMS
   - Or: Phone Numbers → Manage → Get Numbers
   - Order a new number with WhatsApp capability

2. **Setup Sandbox (Faster, for testing):**
   - Console → Messaging → Try it Out → WhatsApp
   - It gives you a sandbox number like `+14155238886` (you have this!)
   - Scan QR code or send sandbox join code to users
   - Users message: `join <code>` to sandbox

3. **Setup Production WhatsApp Business Account (Later):**
   - Apply for Meta WhatsApp Business API
   - Takes 5-10 business days for approval
   - Then move from sandbox to production

---

## Phase 3: Environment Configuration ✅

### Create `.env.production`:
```bash
# Google Pro API (Get from Phase 1)
GOOGLE_API_KEY=AIza_YOUR_NEW_PRODUCTION_KEY_HERE
GEMINI_MODEL=models/gemini-2.0-flash

# Twilio (use YOUR OWN values from https://console.twilio.com)
TWILIO_ACCOUNT_SID=AC_YOUR_ACCOUNT_SID_HERE
TWILIO_AUTH_TOKEN=YOUR_AUTH_TOKEN_HERE
TWILIO_WHATSAPP_NUMBER=+14155238886

# App Settings
DEBUG=False
HOST=0.0.0.0
PORT=5000
FLASK_ENV=production

# Security
SECRET_KEY=generate_a_long_random_string_here
ALLOWED_ORIGINS=https://yourdomain.com

# Render Deployment
DATABASE_URL=postgresql://... (if using database)
```

### Security Notes:
- Never commit secrets to git
- Use Render's environment variables feature
- Rotate secrets quarterly
- Remove old API keys from .env after migration

---

## Phase 4: Add WhatsApp Handler to app.py ✅

**See: `app_whatsapp_handler.py` for the new endpoint**

This adds:
```python
@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    # Receives messages from Twilio
    # Sends to chat engine
    # Replies via Twilio back to user
```

---

## Phase 5: Deploy to Render ✅

### Setup Steps:

1. **Install Render CLI (optional):**
   ```bash
   npm install -g @render-com/cli
   ```

2. **Create `render.yaml` in project root:**
   (See: `render.yaml` file in repo)

3. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Production deployment setup"
   git push origin main
   ```

4. **Connect Render to GitHub:**
   - Go to [render.com](https://render.com)
   - Sign up → Connect GitHub
   - Select `SOPIA_0.2` repo
   - Click "Deploy"

5. **Configure Environment Variables:**
   - Render Dashboard → Environment
   - Add all variables from `.env.production`
   - DO NOT paste raw secrets - use Render's secret manager

6. **Set Webhook URL:**
   - After deployment, Render gives you URL: `https://sopia.onrender.com`
   - Go to Twilio Console → Messaging → WhatsApp Sandbox
   - Webhook URL: `https://sopia.onrender.com/whatsapp`
   - Method: POST
   - Save

---

## Phase 6: Test WhatsApp Integration ✅

1. **Add your number to sandbox:**
   - Message Twilio sandbox join code to your WhatsApp number
   - Confirm: "You are connected to the Twilio sandbox"

2. **Test message:**
   - Message: "What is AHD?" to the sandbox number
   - Should get response from SOPiA

3. **Monitor logs:**
   - Render Dashboard → Logs
   - Watch real-time responses

---

## Production Checklist

- [ ] Google Pro API key obtained and configured
- [ ] Twilio WhatsApp sandbox setup
- [ ] WhatsApp webhook handler added to code
- [ ] GitHub repository created (with .gitignore for .env)
- [ ] Render account created and connected
- [ ] Environment variables set in Render dashboard
- [ ] Webhook URL configured in Twilio
- [ ] Test message sent successfully
- [ ] Error logging configured
- [ ] Rate limiting enabled
- [ ] Monitoring/alerts setup

---

## Cost Breakdown (Monthly)

| Service | Free | Cost |
|---------|------|------|
| Google Gemini Pro | $0 (expired) | $20-100+ |
| Twilio WhatsApp | Sandbox free | $0.005/msg (pay-as-you-go) |
| Render (Web Service) | 750 hrs free | $7-25+ |
| **Total** | - | **~$30-150+** |

---

## Common Issues & Solutions

### "401 Unauthorized" from Gemini
- [ ] Check API key in Render env vars
- [ ] Verify billing is enabled in Google Cloud
- [ ] Check API is enabled: APIs & Services

### WhatsApp messages not received
- [ ] Verify webhook URL in Twilio console
- [ ] Check Render logs for errors
- [ ] Ensure Twilio credentials are correct

### Slow responses
- [ ] Increase Render instance size
- [ ] Enable caching in knowledge base
- [ ] Optimize chunk retrieval (top_k=8)

---

## Next Steps

1. **Start with Phase 1**: Get Google Pro API key
2. **Phase 2**: Setup Twilio sandbox
3. **Update code** with WhatsApp handler
4. **Test locally**: `python app.py`
5. **Deploy to Render**: Connect GitHub
6. **Go Live**: Configure webhook and announce!

