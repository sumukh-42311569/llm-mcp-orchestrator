import os
import google.generativeai as genai

class GeminiAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-pro")

    async def summarize(self, text: str) -> str:
        prompt = f"Summarize the following text:\n\n{text}"
        response = self.model.generate_content(prompt)
        return response.text.strip()

    async def explain_code(self, code: str) -> str:
        prompt = f"Explain this code step by step:\n\n{code}"
        response = self.model.generate_content(prompt, request_options={"timeout": 300})
        return response.text.strip()
