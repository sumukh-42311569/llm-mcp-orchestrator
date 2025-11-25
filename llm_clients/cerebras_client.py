import requests
import os
import httpx

class CerebrasClient:
    def __init__(self):
        self.api_key = os.getenv("CEREBRAS_API_KEY")
        self.url = "https://api.cerebras.ai/v1/chat/completions"

        if not self.api_key:
            raise ValueError("CEREBRAS_API_KEY is not set")

    async def generate(self, messages, model="llama3.1-8b", max_tokens=512, temperature=0.7):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        #These are the exact payload arguments required by cerebras.
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        async with httpx.AsyncClient(timeout=300) as client:
            resp=await client.post(self.url, json= payload, headers= headers)
            return resp.json()
        
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
