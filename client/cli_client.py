import asyncio
import json
import sys
import argparse
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def call_tool(session, tool_name, arguments):
    result = await session.call_tool(tool_name, arguments)
    
    if result.content:
        for item in result.content:
            if hasattr(item, 'text'):
                return json.loads(item.text)
    
    return result


async def orchestrate_task(session, task):
    print(f"\nCreating plan for: {task}")
    
    plan_result = await call_tool(session, "create_plan", {
        "text": task
    })
    
    print(f"Plan created (id={plan_result.get('plan_id')})")
    
    plan_id = plan_result.get("plan_id")
    if not plan_id:
        print("Failed to create plan")
        return
    
    print(f"Executing plan...")
    exec_result = await call_tool(session, "execute_plan", {
        "plan_id": plan_id,
        "stop_on_failure": True
    })
    
    print(f"\nExecution complete!")
    print(json.dumps(exec_result, indent=2))


async def call_specific_tool(session, tool_name, args):
    print(f"\nCalling tool: {tool_name}")
    result = await call_tool(session, tool_name, args)
    print(json.dumps(result, indent=2))


async def main():
    import os
    
    parser = argparse.ArgumentParser(description="MCP Client")
    parser.add_argument("task", nargs="?", help="Task to orchestrate")
    parser.add_argument("--tool", help="Specific tool to call")
    parser.add_argument("--args", help="JSON arguments for the tool")
    
    args = parser.parse_args()
    
    if not args.task and not args.tool:
        parser.error("Either provide a task or use --tool to call a specific tool")
    
    
    # Server should be run as module, else it will not run
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "hub.hub_server"],
        env=os.environ.copy()
    )
    
    print("Connecting to MCP Relay Hub...")
    
    async with AsyncExitStack() as stack:
        stdio_transport = await stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        
        session = await stack.enter_async_context(ClientSession(stdio, write))
        await session.initialize()
        
        print("Connected!")
        
        try:
            if args.tool:
                tool_args = json.loads(args.args) if args.args else {}
                await call_specific_tool(session, args.tool, tool_args)
            else:
                await orchestrate_task(session, args.task)
        
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
