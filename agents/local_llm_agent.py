from llm_clients.local_llm_client import LocalLLMClient
import json

class LocalLLMGeneratedAgent:
    def __init__(self, model="llama3:latest"):
        self.client = LocalLLMClient(model=model)


    def makeLLMResponseString(self, response):

        # If the response id not dict, then return the string of response
        if not isinstance(response, dict):
            return str(response)
        
        # If returned as content then return as content.
        if isinstance(response.get("content"), str) and response.get("content").strip():
            return response["content"]
        
        for key in ("response", "generated_text", "text", "content"):
            val = response.get(key)
            if isinstance(val, str) and val.strip():
                return val
        msg = response.get("message")
        if isinstance(msg, dict):
            c = msg.get("content")
            if isinstance(c, str) and c.strip():
                return c
        results = response.get("results")
        if isinstance(results, list) and results:
            first = results[0]
            if isinstance(first, dict):
                for k in ("content", "text", "response"):
                    v = first.get(k)
                    if isinstance(v, str) and v.strip():
                        return v
                # maybe the dict is just text then return it
                for v in first.values():
                    if isinstance(v, str) and v.strip():
                        return v 
        pieces = []
        for k, v in response.items():
            if isinstance(v, str) and v.strip():
                pieces.append(v.strip())
        if pieces:
            return " ".join(pieces)
        
        # if parsing didn't work, just dump the json
        try:
            return json.dumps(response, ensure_ascii=False)
        except Exception:
            return str(response)

    async def run(self, prompt):
        response = await self.client.generate(prompt)
        if not isinstance(response, dict):
            return self.makeLLMResponseString({"content": str(response)})
        return self.makeLLMResponseString(response)
    
    async def summarize(self, text):
        prompt = "Summarize the following text properly:\n\n" + text
        return await self.run(prompt)

    async def enhance_text(self, text: str) -> str:
        prompt = (
            "Improve the following text with better clarity, detail, and structure:\n\n"
            f"{text}"
        )
        return await self.run(prompt)

    async def general_reasoning(self, problem: str) -> str:
        prompt = f"Think step-by-step and provide a solution:\n\n{problem}"
        return await self.run(prompt)
