from fastapi import FastAPI
from pydantic import BaseModel
from agents.gemini_agent import GeminiAgent
from agents.groq_agent import GroqAgent
from agents.local_llm_agent import LocalLLMGeneratedAgent

app = FastAPI(title="MCP Relay Hub")

gemini_agent = GeminiAgent()
groq_agent = GroqAgent()
local_agent = LocalLLMGeneratedAgent()

class TaskRequest(BaseModel):
    task_type: str
    content: str

@app.post("/process/")
async def process_task(request: TaskRequest):
    if request.task_type == "summarize":
        result = await gemini_agent.summarize(request.content)

    elif request.task_type == "explain_code":
        result = await groq_agent.explain_code(request.content)

    elif request.task_type == "generate_code":
        result = await groq_agent.generate_code(request.content)
        
    elif request.task_type == "enhance_text":
        result = await local_agent.enhance_text(request.content)

    elif request.task_type == "reason":
        result = await local_agent.general_reasoning(request.content)
    else:
        result = "Unknown task type."

    return {"result": result}
