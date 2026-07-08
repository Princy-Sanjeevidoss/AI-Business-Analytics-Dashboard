import os
from typing import Any, Dict

import requests

from backend.config import OPENAI_API_KEY


class AIService:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or OPENAI_API_KEY

    def chat(self, message: str) -> Dict[str, Any]:
        if not self.api_key:
            return {"reply": "AI is not configured. Set OPENAI_API_KEY in the environment."}
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": message}],
                    "temperature": 0.2,
                },
                timeout=20,
            )
            response.raise_for_status()
            data = response.json()
            return {"reply": data["choices"][0]["message"]["content"]}
        except Exception as exc:
            return {"reply": f"AI request failed: {exc}"}

    def business_insights(self, prompt: str) -> Dict[str, Any]:
        return self.chat(prompt)
