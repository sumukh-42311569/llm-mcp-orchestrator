from hub.context_store import ContextStore
from agents.planner_agent import PlannerAgent
from agents.executor_agent import ExecutorAgent
import asyncio
import json
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent



store = ContextStore()
planner = PlannerAgent()
executor = ExecutorAgent(store)

app = Server("mcp-relay-hub")


@app.list_tools()
async def handle_list_tools():
    return [
        Tool(
            name="create_plan",
            description="Create a new execution plan from a task description. Returns plan_id and plan structure.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Task description to plan for"
                    },
                    "refine_with_local": {
                        "type": "boolean",
                        "description": "Whether to refine plan with local LLM",
                        "default": True
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="execute_plan",
            description="Execute a saved plan by plan_id. Returns execution results and aggregated output.",
            inputSchema={
                "type": "object",
                "properties": {
                    "plan_id": {
                        "type": "integer",
                        "description": "ID of the plan to execute"
                    },
                    "stop_on_failure": {
                        "type": "boolean",
                        "description": "Stop execution if a step fails",
                        "default": True
                    }
                },
                "required": ["plan_id"]
            }
        ),
        Tool(
            name="get_plan",
            description="Retrieve a plan and its execution steps by plan_id.",
            inputSchema={
                "type": "object",
                "properties": {
                    "plan_id": {
                        "type": "integer",
                        "description": "ID of the plan to retrieve"
                    }
                },
                "required": ["plan_id"]
            }
        )
    ]


@app.call_tool()
async def handle_call_tool(name, arguments):
    try:
        if name == "create_plan":
            text = arguments.get("text")
            print(f"Creating plan for: {text[:100]}...")
            plan_obj = await planner.plan(text)
            
            if plan_obj is None:
                error_msg = "Planner returned None - plan creation failed"
                print(f"ERROR: {error_msg}")
                return [TextContent(type="text", text=json.dumps({"error": error_msg}))]
            
            print(f"Plan object received: {json.dumps(plan_obj)[:200]}...")
            plan_id = store.save_plan(input_text=text, plan_json=plan_obj, meta_data={})
            print(f"Plan saved with ID: {plan_id}")
            
            result = {
                "plan_id": plan_id,
                "plan": plan_obj,
                "status": "created"
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "execute_plan":
            plan_id = arguments.get("plan_id")
            
            print(f"Executing plan {plan_id}...")
            result = await executor.execute_plan(plan_id)
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_plan":
            plan_id = arguments.get("plan_id")
            plan = store.get_plan(plan_id)
            steps = store.get_steps_for_plan(plan_id)
            result = {"plan": plan, "steps": steps}
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        else:
            return [TextContent(type="text", text=json.dumps({"error": f"Tool doesn't exisit: {name}"}))]
    
    except Exception as e:
        print(f"Error executing tool {name}: {e}")
        import traceback
        traceback.print_exc()
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def main():
    print("Starting MCP Orchestrator Hub (stdio)")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-relay-hub",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
