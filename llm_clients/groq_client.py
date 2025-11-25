import os
from groq import Groq
import httpx

class GroqClient:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        self.url="https://api.groq.com/openai/v1/chat/completions"

    async def generate(self, messages, model="llama-3.1-8b-instant", temperature=0.6, max_tokens=512):
        headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(self.url, json=payload, headers=headers)
            return response.json()
        
# small response parser    
def getResponseText(jsonResp):
    choices=jsonResp.get("choices")
    if choices:
        c=choices[0]
        msg=c.get("message") if c.get("message") else {}
        if isinstance(msg, dict) and "content" in msg:
            return msg["content"]
        if "text" in c:
            return c["text"]
    for i in ("response", "generated_text", "text", "content"):
        if i in jsonResp:
            return jsonResp[i]
    return str(jsonResp)
