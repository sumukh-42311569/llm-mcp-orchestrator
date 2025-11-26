from llm_clients.cerebras_client import CerebrasClient
from llm_clients.cerebras_client import getResponseText

class CerebrasAgent:
    def __init__(self, name="cerebras-agent", model="llama3.1-8b"):
        self.name = name
        self.model = model
        self.client = CerebrasClient()

    async def run(self, prompt):
        messages = [
            {"role":"system", "content":"You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        response = await self.client.generate(messages=messages, model=self.model)
        return getResponseText(response)
        

    async def summarize(self, text):
        return await self.run("Summarize:\n\n" + text)
