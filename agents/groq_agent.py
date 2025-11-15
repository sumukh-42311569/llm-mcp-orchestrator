from llm_clients.groq_client import GroqClient

class GroqAgent:
    def __init__(self):
        self.client = GroqClient()

    async def generate_code(self, description: str) -> str:
        prompt = f"Write clean and well-commented Python code for the following task:\n{description}"
        return self.client.generate(prompt)

    async def explain_code(self, code: str) -> str:
        prompt = f"Explain this code step by step:\n\n{code}"
        return self.client.generate(prompt)
