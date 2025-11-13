from fastapi import FastAPI
from pydantic import BaseModel
from agents.gemini_agent import GeminiAgent

app = FastAPI(title="MCP Relay Hub")
gemini_agent = GeminiAgent()

class TaskRequest(BaseModel):
    task_type: str
    content: str

@app.post("/process/")
async def process_task(request: TaskRequest):
    if request.task_type == "summarize":
        result = await gemini_agent.summarize(request.content)
    elif request.task_type == "explain_code":
        result = await gemini_agent.explain_code(request.content)
    else:
        result = "Unknown task type."
    return {"result": result}
