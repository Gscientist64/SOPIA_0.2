# whatsapp_handler.py - Twilio WhatsApp Integration
"""
Handle incoming WhatsApp messages from Twilio and route them to the chat engine.
Add this to app.py by importing and registering the routes.
"""

import os
import logging
from flask import request, jsonify
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from typing import Optional, Dict

log = logging.getLogger("SOPiA-WhatsApp")

class WhatsAppHandler:
    """Manage WhatsApp communication via Twilio"""
    
    def __init__(self, chat_engine, llm_client):
        self.chat_engine = chat_engine
        self.llm = llm_client
        
        # Initialize Twilio client
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        
        if not account_sid or not auth_token:
            raise ValueError("❌ Missing Twilio credentials in .env")
        
        self.twilio_client = Client(account_sid, auth_token)
        self.twilio_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "+14155238886")
        
        log.info(f"✅ WhatsApp Handler initialized with Twilio number: {self.twilio_number}")
    
    def handle_incoming_message(self, twilio_request: Dict) -> str:
        """
        Process incoming WhatsApp message from Twilio
        
        Expected POST data from Twilio:
        - From: sender's WhatsApp number (e.g., whatsapp:+1234567890)
        - To: bot's WhatsApp number (e.g., whatsapp:+14155238886)
        - Body: message text
        - MessageSid: unique message ID
        - AccountSid: Twilio account
        """
        try:
            sender = twilio_request.get("From", "").replace("whatsapp:", "")
            recipient = twilio_request.get("To", "").replace("whatsapp:", "")
            message_body = twilio_request.get("Body", "").strip()
            message_sid = twilio_request.get("MessageSid", "unknown")
            
            log.info(f"📨 Incoming message from {sender}: {message_body[:100]}")
            
            if not message_body:
                return self._build_response("Please send a message.")
            
            # Rate limiting: basic check
            if len(message_body) > 10000:
                return self._build_response("Message too long. Please keep it under 10,000 characters.")
            
            # Get response from chat engine
            response = self._get_chat_response(message_body, sender)
            
            # Send response back to user
            self._send_response(sender, response, message_sid)
            
            return self._build_twiml_response(response)
        
        except Exception as e:
            log.error(f"❌ Error handling WhatsApp message: {e}")
            return self._build_twiml_response(
                "Sorry, I encountered an error. Please try again."
            )
    
    def _get_chat_response(self, user_message: str, sender_number: str) -> str:
        """Get response from chat engine"""
        try:
            # You can add patient context here if storing user data
            response = self.chat_engine.answer(user_message)
            
            # Format response with confidence indicator
            confidence = response.confidence if hasattr(response, 'confidence') else 0.5
            answer = response.answer if hasattr(response, 'answer') else str(response)
            
            # Truncate for WhatsApp (character limits)
            max_length = 4096  # WhatsApp max message length
            if len(answer) > max_length:
                answer = answer[:max_length - 20] + "\n\n[Message truncated...]"
            
            # Add confidence indicator if low
            if confidence < 0.5:
                answer += f"\n\n⚠️ Low confidence ({confidence:.0%}). Please verify with medical professional."
            
            log.info(f"✅ Response prepared for {sender_number} (confidence: {confidence:.0%})")
            return answer
        
        except Exception as e:
            log.error(f"❌ Chat engine error: {e}")
            return "Sorry, I couldn't process your question. Please try again."
    
    def _send_response(self, recipient_number: str, message: str, original_sid: str) -> bool:
        """Send response back to user via Twilio"""
        try:
            self.twilio_client.messages.create(
                from_=f"whatsapp:{self.twilio_number}",
                to=f"whatsapp:{recipient_number}",
                body=message
            )
            log.info(f"✅ Message sent to {recipient_number}")
            return True
        
        except Exception as e:
            log.error(f"❌ Failed to send WhatsApp message: {e}")
            return False
    
    def _build_twiml_response(self, message: str) -> str:
        """Build Twilio XML response (required by Twilio)"""
        resp = MessagingResponse()
        resp.message(message)
        return str(resp)
    
    def _build_response(self, message: str) -> str:
        """Build simple response"""
        resp = MessagingResponse()
        resp.message(message)
        return str(resp)

# Integration Code to Add to app.py:
# ===================================
# 
# At the top of app.py, add:
#   from whatsapp_handler import WhatsAppHandler
#
# In the Flask app initialization section, add:
#   whatsapp_handler = None
#
# After chat_engine is initialized, add:
#   whatsapp_handler = WhatsAppHandler(chat_engine, llm_client)
#
# Add this route to app.py:
#
# @app.route("/whatsapp", methods=["GET", "POST"])
# def whatsapp_webhook():
#     '''Webhook endpoint for Twilio WhatsApp messages'''
#     if request.method == "GET":
#         # Twilio verification
#         return "OK", 200
#     
#     # Handle POST (actual messages)
#     global whatsapp_handler
#     if not whatsapp_handler:
#         return jsonify({"error": "WhatsApp handler not initialized"}), 503
#     
#     response = whatsapp_handler.handle_incoming_message(request.form.to_dict())
#     return response, 200
#
