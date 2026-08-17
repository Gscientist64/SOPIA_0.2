# INTEGRATION GUIDE: Add WhatsApp Handler to app.py

## Overview
This guide shows you exactly how to integrate the WhatsApp webhook handler into your existing app.py.

---

## Step 1: Add Imports (at the top of app.py)

**Location:** Line 1-15 in app.py (where other imports are)

**Add these lines:**
```python
# Twilio WhatsApp Support
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
```

---

## Step 2: Initialize WhatsApp Handler (in app initialization section)

**Location:** Around line 1000-1010 where other global variables are initialized

**Find the section that looks like:**
```python
_kb = None
_chat = None
_llm = None
_medical_kb = None
_reasoning_engine = None
```

**Add after these lines:**
```python
_whatsapp_handler = None
```

---

## Step 3: Add WhatsApp Handler Class (before main routes)

**Location:** Before the route handlers start (around line 600-700)

**Add this complete class:**

```python
# ===== WHATSAPP HANDLER =====
class SimpleWhatsAppHandler:
    """Receive WhatsApp messages from Twilio and send responses"""
    
    def __init__(self, chat_engine):
        self.chat_engine = chat_engine
        
        # Initialize Twilio
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        
        if not account_sid or not auth_token:
            print("⚠️  Twilio credentials missing - WhatsApp disabled")
            self.enabled = False
            return
        
        try:
            self.twilio_client = Client(account_sid, auth_token)
            self.whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "+14155238886")
            self.enabled = True
            print(f"✅ WhatsApp Handler initialized with number: {self.whatsapp_number}")
        except Exception as e:
            print(f"❌ Failed to initialize Twilio: {e}")
            self.enabled = False
    
    def handle_message(self, incoming_data):
        """Process incoming WhatsApp message from Twilio"""
        try:
            sender = incoming_data.get("From", "").replace("whatsapp:", "")
            message_body = incoming_data.get("Body", "").strip()
            
            if not message_body or not self.enabled:
                return self._build_twiml("Please send a message.")
            
            # Get response from chat engine
            response = self.chat_engine.answer(message_body)
            answer = response.answer if hasattr(response, 'answer') else str(response)
            
            # Truncate if too long (WhatsApp limit)
            if len(answer) > 4096:
                answer = answer[:4096 - 20] + "\n\n[Message truncated]"
            
            # Send back to user
            try:
                self.twilio_client.messages.create(
                    from_=f"whatsapp:{self.whatsapp_number}",
                    to=f"whatsapp:{sender}",
                    body=answer
                )
                print(f"✅ Message sent to {sender}")
            except Exception as e:
                print(f"❌ Twilio send error: {e}")
            
            return self._build_twiml(answer)
        
        except Exception as e:
            print(f"❌ WhatsApp handler error: {e}")
            return self._build_twiml("Error processing message. Please try again.")
    
    def _build_twiml(self, message):
        """Build Twilio XML response"""
        resp = MessagingResponse()
        resp.message(message)
        return str(resp)
```

---

## Step 4: Add WhatsApp Route (at the end, before `if __name__`)

**Location:** After `/suggestions` route, before `if __name__ == "__main__"`

**Add this route:**

```python
# ===== WHATSAPP WEBHOOK =====
@app.route("/whatsapp", methods=["GET", "POST"])
def whatsapp_webhook():
    """
    Webhook endpoint for Twilio WhatsApp messages
    
    Configure in Twilio Console:
    - Messaging → WhatsApp Sandbox
    - "When a message comes in"
    - URL: https://your-domain.com/whatsapp
    - Method: POST
    """
    global _whatsapp_handler
    
    if request.method == "GET":
        # Twilio verification endpoint
        return "OK", 200
    
    # Handle POST (actual messages)
    if not _whatsapp_handler:
        return jsonify({"error": "WhatsApp handler not initialized"}), 503
    
    try:
        response = _whatsapp_handler.handle_message(request.form.to_dict())
        return response, 200
    except Exception as e:
        print(f"❌ WhatsApp webhook error: {e}")
        return jsonify({"error": str(e)}), 500
```

---

## Step 5: Initialize Handler in _init_if_needed()

**Location:** Find the `_init_if_needed()` function (around line 990)

**Inside this function, after `_chat` is initialized, add:**

```python
    # Initialize WhatsApp handler
    if _chat and not _whatsapp_handler:
        _whatsapp_handler = SimpleWhatsAppHandler(_chat)
```

**Example of what it should look like:**
```python
def _init_if_needed():
    global _kb, _chat, _llm, _medical_kb, _reasoning_engine, _whatsapp_handler
    
    if _chat:
        return  # Already initialized
    
    print("🔧 Initializing SOPiA components...")
    
    # ... existing initialization code ...
    
    # Initialize WhatsApp handler
    if _chat and not _whatsapp_handler:
        _whatsapp_handler = SimpleWhatsAppHandler(_chat)
    
    print("✅ Initialization complete!")
```

---

## Step 6: Test Locally

1. Make sure `.env` has Twilio credentials
2. Run: `python app.py`
3. Test the endpoint:
   ```bash
   curl http://localhost:5050/whatsapp
   # Should return: OK
   ```

---

## Step 7: Configure Twilio Webhook (After Deployment)

Once you deploy to Render:

1. Go to [Twilio Console](https://www.twilio.com/console)
2. Messaging → Try it out → Send a WhatsApp
3. Under "Sandbox Configuration":
   - "When a message comes in":
   - URL: `https://sopia-production.onrender.com/whatsapp`
   - Method: POST
4. Save

---

## ✅ Complete!

Your app now has:
- ✅ WhatsApp message receiving
- ✅ Chat engine integration
- ✅ Automatic reply sending
- ✅ Error handling
- ✅ Message truncation for size limits

---

## Testing Checklist

- [ ] Code added and no syntax errors
- [ ] `python app.py` starts without errors
- [ ] `/whatsapp` endpoint responds with OK
- [ ] Deployed to Render successfully
- [ ] Twilio webhook URL configured
- [ ] Test message sent to sandbox
- [ ] Response received on WhatsApp
- [ ] Message logged in Render console

---

## Troubleshooting

**"Twilio credentials missing"**
- Check `.env` has TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN
- Restart app.py

**"500 error on /whatsapp"**
- Check Render logs for error message
- Verify chat engine is initialized
- Check Twilio credentials are correct

**No message received**
- Verify you've joined the sandbox (send `join CODE`)
- Check Twilio console shows incoming message
- Check Render logs show received request
- Verify response was sent (should see "Message sent to...")

