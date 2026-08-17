# llm_client.py  —  updated for google-genai SDK
import logging
from google import genai
from google.genai.types import GenerateContentConfig

log = logging.getLogger("SOPiA")


class LLMClient:
    def __init__(self, api_key: str, provider: str = "gemini"):
        self.provider = provider.lower().strip()
        self.api_key = api_key
        self.model = None
        self.client = None

        if self.provider == "gemini":
            # ✅ New SDK initialization
            self.client = genai.Client(api_key=self.api_key)
            # Use the correct model names for the new SDK
            self.model = "gemini-2.0-flash"  # or "gemini-1.5-flash" if available
            log.info(f"🤖 Google GenAI ({self.model}) initialized successfully.")
        
        elif self.provider == "openai":
            import openai
            openai.api_key = self.api_key
            self.model = "gpt-4o-mini"
            self.client = openai
            log.info("🤖 OpenAI GPT model initialized successfully.")

        else:
            raise ValueError(f"❌ Unknown provider: {self.provider}")

    def generate(self, prompt: str) -> str:
        """Generate text content using the configured LLM provider."""
        try:
            if self.provider == "gemini":
                # Correct way with new SDK
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=GenerateContentConfig(
                        temperature=0.3,
                        max_output_tokens=2048,
                    ),
                )
                return response.text.strip()

            elif self.provider == "openai":
                # Your existing OpenAI code
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )
                return response.choices[0].message.content.strip()

        except Exception as e:
            log.error(f"❌ LLM generation failed: {e}")
            return ""