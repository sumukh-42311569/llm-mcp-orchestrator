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
        
        fulltext = ""

        try:
            async with httpx.AsyncClient(timeout=300) as client:
                async with client.stream("POST", self.api_url, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        # ignore empty lines
                        if not line.strip():
                            continue
                        
                        data = json.loads(line) 

                        for k in ["response", "content", "text", "generated_text"]:
                            if k in data and isinstance(data[k], str):
                                fulltext += data[k]

                        # Ollama style
                        if "message" in data and isinstance(data["message"], dict):
                            if "content" in data["message"]:
                                fulltext += data["message"]["content"]
                
                # Check after stream is complete
                if fulltext.strip() == "":
                    return {
                        "error": "Empty response from local LLM",
                        "content": ""
                    }

                return {"content": fulltext}
        except httpx.ConnectError as e:
            return {
                "error": f"Cannot connect to local LLM at {self.api_url}. Is Ollama running?",
                "content": ""
            }
        except Exception as e:
            return {
                "error": f"Local LLM error: {str(e)}",
                "content": ""
            }    
