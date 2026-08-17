# 📋 Production Deployment Checklist

## Phase 1: API Setup ✅

### Google Pro Configuration
- [ ] Google Pro subscription purchased and active
- [ ] Google Cloud Console project created: "SOPIA_Production"
- [ ] Generative AI API enabled in project
- [ ] API Key generated and copied
- [ ] Billing enabled and Google Pro subscription linked
- [ ] Tested API key works (status code 200)

### Twilio WhatsApp Setup
- [ ] Twilio account has active credit/subscription
- [ ] Account SID and Auth Token saved in .env
- [ ] WhatsApp Sandbox number noted (+1415...)
- [ ] WhatsApp Sandbox join code obtained
- [ ] Tested: Can join sandbox from personal WhatsApp

---

## Phase 2: Code Updates ✅

### Security
- [ ] `.env` file created with actual API keys
- [ ] `.env.example` created without secrets
- [ ] `.gitignore` configured to exclude .env
- [ ] All API keys rotated (old free keys removed)
- [ ] No hardcoded secrets in code

### WhatsApp Integration
- [ ] `whatsapp_handler.py` added to project
- [ ] WhatsApp route added to `app.py`:
  - [ ] Imports added at top
  - [ ] Global handler variable declared
  - [ ] Handler class added
  - [ ] `/whatsapp` route implemented
  - [ ] Handler initialized in `_init_if_needed()`

### Production Configuration
- [ ] `requirements-production.txt` created with gunicorn
- [ ] `render.yaml` created for Render deployment
- [ ] `QUICK_START.md` reviewed
- [ ] `INTEGRATION_WHATSAPP.md` reviewed
- [ ] `PRODUCTION_SETUP.md` reviewed

### Testing
- [ ] Code runs locally: `python app.py`
- [ ] GET /health returns 200 OK
- [ ] POST /whatsapp returns 200 OK with Twilio response
- [ ] Chat engine responds to test questions
- [ ] No errors in console

---

## Phase 3: Deployment Setup ✅

### GitHub
- [ ] Repository created on GitHub
- [ ] All files added: `git add .`
- [ ] Initial commit: `git commit -m "Initial setup"`
- [ ] Pushed to main branch: `git push origin main`
- [ ] `.env` NOT in git (verify .gitignore works)

### Render Account
- [ ] Render account created (render.com)
- [ ] Logged in with GitHub account
- [ ] SOPIA repository authorized to Render

### Render Deployment
- [ ] New Web Service created from SOPIA repo
- [ ] Python 3.11 runtime selected
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command: `gunicorn --workers 3 app:app`
- [ ] Environment variables configured:
  - [ ] GOOGLE_API_KEY
  - [ ] TWILIO_ACCOUNT_SID
  - [ ] TWILIO_AUTH_TOKEN
  - [ ] TWILIO_WHATSAPP_NUMBER
  - [ ] DEBUG=False
  - [ ] FLASK_ENV=production

### Render Verification
- [ ] Deployment successful (no build errors)
- [ ] Service URL obtained: https://sopia-*.onrender.com
- [ ] Health check: https://sopia-*.onrender.com/health → 200 OK
- [ ] Chat endpoint: POST to /chat works
- [ ] No 500 errors in logs

---

## Phase 4: Twilio Configuration ✅

### Webhook Configuration
- [ ] Logged into Twilio Console
- [ ] Navigated to Messaging → WhatsApp Sandbox
- [ ] Under "Sandbox Configuration":
  - [ ] "When a message comes in" URL: `https://sopia-*.onrender.com/whatsapp`
  - [ ] Method: POST
  - [ ] Saved configuration

### Sandbox Testing
- [ ] Sent test message to sandbox from WhatsApp
- [ ] Received response from SOPiA
- [ ] Message logged in Render dashboard
- [ ] Response visible in Render logs

---

## Phase 5: Production Validation ✅

### Functional Testing
- [ ] Medical question answered accurately
- [ ] Response includes relevant sources
- [ ] Confidence score displayed when low
- [ ] Message truncated if too long (> 4096 chars)
- [ ] Follow-up suggestions included
- [ ] Error messages are helpful if question fails

### Performance Testing
- [ ] Response time < 10 seconds for typical question
- [ ] No timeout errors (120s timeout configured)
- [ ] Concurrent messages handled (multiple users)
- [ ] Render CPU/memory usage reasonable

### Security Testing
- [ ] API keys not logged or exposed
- [ ] Twilio messages authenticated (from correct number)
- [ ] No sensitive data in error messages
- [ ] Rate limiting working (if configured)

### Logging & Monitoring
- [ ] Render logs show incoming messages
- [ ] Errors logged with timestamps
- [ ] No exposed stack traces in responses
- [ ] Can filter logs by severity

---

## Phase 6: Go-Live Preparation ✅

### Documentation
- [ ] User guide created (how to use WhatsApp bot)
- [ ] FAQ document prepared
- [ ] Support contact information shared
- [ ] Limitations explained (sandbox vs production)

### Backup & Recovery
- [ ] Knowledge base backed up
- [ ] Database backups configured (if using DB)
- [ ] Disaster recovery plan documented

### Monitoring Setup
- [ ] Error alerts configured (optional)
- [ ] Usage metrics tracked
- [ ] Daily log review scheduled

---

## Phase 7: Launch ✅

### Pre-Launch
- [ ] Final testing with test users
- [ ] All checklist items verified
- [ ] Team trained on system
- [ ] Support ready

### Launch
- [ ] Sandbox join code shared with users
- [ ] Users test and verify
- [ ] Collect initial feedback

### Post-Launch
- [ ] Monitor first 24 hours closely
- [ ] Respond to user issues immediately
- [ ] Log all errors for analysis
- [ ] Plan improvements based on feedback

---

## Production Improvements (Post-Launch)

After successful launch, consider:

### Short-term (Week 1-2)
- [ ] Optimize response times based on metrics
- [ ] Add more example questions to suggestions
- [ ] Improve error messages based on user feedback
- [ ] Enable detailed monitoring/logging

### Medium-term (Week 2-4)
- [ ] Migrate from Sandbox to WhatsApp Business Account (requires Meta approval)
- [ ] Add user authentication/patient profile tracking
- [ ] Implement message history/conversation context
- [ ] Add admin dashboard for usage analytics

### Long-term (Month 1+)
- [ ] Upgrade Render tier if traffic increases
- [ ] Add database for user data persistence
- [ ] Implement HIPAA compliance (if medical data)
- [ ] Setup CI/CD for automated deployments
- [ ] Add A/B testing for prompt improvements
- [ ] Expand knowledge base with more SOPs

---

## Cost Monitoring

After deployment, track these monthly costs:

| Service | Estimated | Actual |
|---------|-----------|--------|
| Google Gemini | $10-30 | |
| Twilio WhatsApp | $5-20 | |
| Render Hosting | $7-25 | |
| **Total** | **$22-75** | |

Set budget alerts in:
- Google Cloud Console
- Twilio Dashboard
- Render Dashboard

---

## Emergency Contacts

- **Google Cloud Support:** [support.google.com](https://support.google.com)
- **Twilio Support:** [twilio.com/console/support](https://www.twilio.com/console/support)
- **Render Support:** [render.com/support](https://render.com/support)

---

## Final Sign-Off

- [ ] Project Lead: _________________ Date: _______
- [ ] Tech Lead: _________________ Date: _______
- [ ] QA Verified: _________________ Date: _______

---

## Notes

```
[Add any project-specific notes here]
```

