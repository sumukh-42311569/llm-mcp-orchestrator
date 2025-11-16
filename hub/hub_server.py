from fastapi import FastAPI
from pydantic import BaseModel
from agents.gemini_agent import GeminiAgent
from agents.groq_agent import GroqAgent
from agents.local_llm_agent import LocalLLMGeneratedAgent
from hub.context_store import ContextStore

app = FastAPI(title="MCP Relay Hub")

gemini_agent = GeminiAgent()
groq_agent = GroqAgent()
local_agent = LocalLLMGeneratedAgent()
context_store = ContextStore()

class TaskRequest(BaseModel):
    task_type: str
    content: str

@app.post("/process/")
async def process_task(request: TaskRequest):
    if request.task_type == "summarize":
        agent = "gemini"
        result = await gemini_agent.summarize(request.content)

    elif request.task_type == "explain_code":
        agent = "groq"
        result = await groq_agent.explain_code(request.content)

    elif request.task_type == "generate_code":
        agent = "groq"
        result = await groq_agent.generate_code(request.content)
        
    elif request.task_type == "enhance_text":
        agent = "local_llm"
        result = await local_agent.enhance_text(request.content)

    elif request.task_type == "reason":
        agent = "local_llm"
        result = await local_agent.general_reasoning(request.content)
    else:
        result = "Unknown task type."
        return {"result": result}

    # Save in db before returning the response.
    context_store.save_record(
        task_type=request.task_type,
        input_content=request.content,
        agent_used=agent,
        output_content=result,
        metadata={"status": "success"}
    )

    return {"result": result, "agent_used": agent}

# Get previous records.
@app.get("/history/")
async def history(limit: int = 10):
    records = context_store.get_last_records(limit)
    return [
        {
            "id": r.id,
            "task_type": r.task_type,
            "agent_used": r.agent_used,
            "input": r.input_content,
            "output": r.output_content,
            "timestamp": r.timestamp,
        }
        for r in records
    ]
