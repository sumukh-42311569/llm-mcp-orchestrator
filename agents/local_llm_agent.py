from llm_clients.local_llm_client import LocalLLMClient

class LocalLLMGeneratedAgent:
    def __init__(self, model="llama3:latest"):
        self.client = LocalLLMClient(model=model)

    async def enhance_text(self, text: str) -> str:
        prompt = (
            "Improve the following text with better clarity, detail, and structure:\n\n"
            f"{text}"
        )
        return self.client.generate(prompt)

    async def general_reasoning(self, problem: str) -> str:
        prompt = f"Think step-by-step and provide a solution:\n\n{problem}"
        return self.client.generate(prompt)
