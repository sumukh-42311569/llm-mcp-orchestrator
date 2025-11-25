from llm_clients.groq_client import GroqClient
from llm_clients.groq_client import getResponseText

class GroqAgent:
    def __init__(self):
        self.client = GroqClient()

    async def run(self, prompt):
        messages = [
            {"role": "system", "content": "You are a helpful coding assistant."},
            {"role": "user", "content": prompt}
        ]
        response = await self.client.generate(messages)
        return getResponseText(response)

    async def generate_code(self, description):
        prompt = f"Write clean and well-commented Python code for the following task:\n{description}"
        return await self.run(prompt)

    async def explain_code(self, code: str) -> str:
        prompt = f"Explain this code step by step:\n\n{code}"
        return await self.run(prompt)