from llm_clients.cerebras_client import CerebrasClient

class CerebrasAgent:
    def __init__(self, name="cerebras-agent", model="llama3.1-8b"):
        self.name = name
        self.model = model
        self.client = CerebrasClient()

    def run(self, prompt):
        messages = [
            {"role": "user", "content": prompt}
        ]
        return self.client.generate(messages, model=self.model)

    async def rewrite(self, text):
        prompt = f"Rewrite the following text in a clearer and more concise way:\n\n{text}"
        return self.run(prompt)

    async def answer_question(self, question):
        prompt = f"Answer the following question:\n\n{question}"
        return self.run(prompt)
