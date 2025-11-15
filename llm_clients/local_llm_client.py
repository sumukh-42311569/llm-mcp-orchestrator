import requests
import json

class LocalLLMClient:
    def __init__(self, model="llama3:latest"):
        self.model = model
        self.api_url = "http://localhost:11434/api/generate"  

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(self.api_url, json=payload, timeout=30000)
        response.raise_for_status()
        data = response.json()

        return data.get("response", "")
