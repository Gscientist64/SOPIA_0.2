# QUICK START: Setup Google Pro API & Deploy to WhatsApp

## ⏱️ Time Required: 30 minutes

---

## Step 1: Get Google Pro API Key (5 min)

### Option A: Use Existing Google Account with Pro Subscription

1. Go to **[Google Cloud Console](https://console.cloud.google.com/)**
2. **Create a new project:**
   - Click "Select a Project" at top-left
   - Click "New Project"
   - Name: `SOPIA_Production`
   - Click "Create"
3. **Enable Gemini API:**
   - Search bar → type "Generative AI"
   - Click "Generative AI API"
   - Click "Enable"
4. **Create API Key:**
   - Left sidebar → "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy the key (looks like: `AIza...`)
5. **Enable Billing:**
   - Sidebar → "Billing"
   - Link your Google Pro subscription
   - Confirm billing is active

### ✅ Your Google Pro API Key is ready!

---

## Step 2: Update Environment File (3 min)

1. Open `.env` in VS Code
2. Replace the first `GOOGLE_API_KEY` with your new key:
   ```
   GOOGLE_API_KEY=AIza_YOUR_NEW_KEY_HERE
   ```
3. Keep the Twilio credentials as-is (they're already correct)
4. Save the file

---

## Step 3: Test Locally (5 min)

1. Open terminal in VS Code
2. Run:
   ```bash
   python app.py
   ```
3. Go to `http://localhost:5000/health`
4. Should see: `{"message": "✅ SOPiA Server is running", ...}`

---

## Step 4: Setup Twilio WhatsApp Sandbox (10 min)

### Prerequisite:
- Twilio Account (you already have one)
- Your personal WhatsApp number

### Steps:

1. Go to **[Twilio Console](https://www.twilio.com/console)**
2. Navigate to **Messaging → Try it out → Send a WhatsApp**
3. You'll see a sandbox number like `+14155238886` (already in your .env)
4. **Join the sandbox:**
   - Message to that number: `join <CODE>`
   - (The code is shown in the console)
5. Wait for confirmation: "You are connected to..."
6. Now you can test!

---

## Step 5: Deploy to Render (10 min)

### Prerequisites:
- GitHub account with your code repo
- Render account ([render.com](https://render.com))

### Steps:

1. **Push code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Production setup with WhatsApp handler"
   git push origin main
   ```

2. **Connect Render to GitHub:**
   - Go to [render.com](https://render.com)
   - Sign up (use GitHub to login)
   - Click "New +" → "Web Service"
   - Select your SOPIA repository
   - Click "Connect"

3. **Configure Build & Deploy:**
   - **Name:** `sopia-production`
   - **Environment:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --workers 3 app:app`
   - **Plan:** Select "Free" tier

4. **Add Environment Variables:**
   - Scroll to "Environment Variables"
   - Click "Add from .env"
   - Or add manually:
     | Key | Value |
     |-----|-------|
     | GOOGLE_API_KEY | AIza_YOUR_KEY |
     | TWILIO_ACCOUNT_SID | AC... |
     | TWILIO_AUTH_TOKEN | a6e3... |
     | TWILIO_WHATSAPP_NUMBER | +14155238886 |
     | DEBUG | False |
     | FLASK_ENV | production |

5. **Deploy:**
   - Click "Create Web Service"
   - Wait 2-3 minutes for deployment
   - You'll get URL: `https://sopia-production.onrender.com`

---

## Step 6: Configure Twilio Webhook (5 min)

1. After Render deployment, copy your URL: `https://sopia-production.onrender.com`

2. Go back to **[Twilio Console](https://www.twilio.com/console)**

3. Navigate to **Messaging → WhatsApp Sandbox**

4. Under "Sandbox Configuration":
   - **When a message comes in:** 
     - URL: `https://sopia-production.onrender.com/whatsapp`
     - Method: POST
   - Click "Save"

5. Test it! Send a message to the sandbox number from your WhatsApp

---

## ✅ You're Live!

Users can now:
1. Get the sandbox join code from your Twilio console
2. Message `join <CODE>` to `+14155238886`
3. Ask questions about HIV/AIDS care protocols
4. Get instant answers from SOPiA!

---

## 📊 Cost Estimation

| Service | Free | Paid |
|---------|------|------|
| Google Gemini | $0 (expired) | $0.075 per 1M input tokens |
| Twilio WhatsApp | Sandbox free | $0.005 per message |
| Render | 750 hrs/month | $7/month minimum |
| **Total** | - | **$10-50/month** |

### Example: 1000 messages/month
- Google: ~$2 (depends on message length)
- Twilio: $5
- Render: $7
- **Total: ~$14/month**

---

## 🐛 Troubleshooting

### "Invalid API Key"
- Go to Google Cloud Console
- Check if billing is enabled
- Regenerate key and update .env

### WhatsApp messages not received
- Check Render logs: Dashboard → Logs
- Verify webhook URL in Twilio console
- Make sure `/whatsapp` endpoint is added to app.py

### Slow responses
- Check Render CPU usage
- May need to upgrade from Free tier
- Or optimize knowledge base chunk retrieval

---

## 📞 Support Channels

- **Google Cloud Help:** [support.google.com](https://support.google.com)
- **Twilio Docs:** [twilio.com/docs](https://twilio.com/docs)
- **Render Docs:** [render.com/docs](https://render.com/docs)
- **This Project Issues:** Add to GitHub Issues

---

## Next: Production Improvements

After going live, consider:
- [ ] Move from Sandbox to WhatsApp Business Account (needs Meta approval)
- [ ] Add user authentication/patient records
- [ ] Implement caching for faster responses
- [ ] Setup error logging/monitoring
- [ ] Add rate limiting per user
- [ ] Backup/disaster recovery
- [ ] HIPAA compliance (if medical data)

