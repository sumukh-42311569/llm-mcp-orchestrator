import requests
import os

class CerebrasClient:
    def __init__(self):
        self.api_key = os.getenv("CEREBRAS_API_KEY")
        self.url = "https://api.cerebras.ai/v1/chat/completions"

        if not self.api_key:
            raise ValueError("CEREBRAS_API_KEY is missing.")

    def generate(self, messages, model="Qwen-3-32B", temperature=0.7):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }

        response = requests.post(self.url, headers=headers, json=payload)
        response.raise_for_status()

        output = response.json()
        return output["choices"][0]["message"]["content"]
