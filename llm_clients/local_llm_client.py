import requests
import json
import httpx

class LocalLLMClient:
    def __init__(self, model="llama3:latest"):
        self.model = model
        self.api_url = "http://localhost:11434/api/generate"  

    async def generate(self, prompt):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True
        }

        async with httpx.AsyncClient(timeout=300) as client:
            async with client.stream("POST", self.api_url, json=payload) as response:
                async for line in response.aiter_lines():
                    # ignore empty lines
                    if not line.strip():
                        continue
                    # ignore if json not valid
                    try:
                        data=json.loads(line)
                    except Exception:
                        continue 

                    for k in ["response", "content", "text", "generated_text"]:
                            if k in data and isinstance(data[k], str):
                                fulltext += data[k]

                    # Ollama style
                    if "message" in data and isinstance(data["message"], dict):
                            if "content" in data["message"]:
                                fulltext += data["message"]["content"]
                if fulltext.strip() == "":
                        # if llm returns empty response, return error.
                        return {
                            "error": "Empty response from local LLM",
                            "content": ""
                        }

                return {"content": fulltext}    
