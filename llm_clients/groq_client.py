import os
from groq import Groq

class GroqClient:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        self.client = Groq(api_key=api_key)

    def generate(self, prompt: str, model: str = "openai/gpt-oss-20b"):
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6
        )
        return response.choices[0].message.content
