from hub.context_store import ContextStore
from agents.cerebras_agent import CerebrasAgent
from agents.groq_agent import GroqAgent
from agents.local_llm_agent import LocalLLMGeneratedAgent
import json
import time

agents = {"cerebras": CerebrasAgent(),
        "groq": GroqAgent(),
        "local": LocalLLMGeneratedAgent(),
        }

class ExecutorAgent:
    def __init__(self, store=None):
        self.store = store or ContextStore()

    async def execute_plan(self, planID):
        plan = self.store.get_plan(planID)
        plan_json = plan["plan_json"]
        steps = plan_json.get("plan") if isinstance(plan_json, dict) else plan_json
        results = []

        for s in steps:
            idx = s.get("step_index", 0)
            agent_name = s.get("agent", "local")
            action = s.get("action", "run")
            input_data = s.get("input")

            print(f"Executor: Step {idx} - routing to '{agent_name}' for action '{action}'")
            step_id = self.store.add_step(planID, idx, agent_name, action, {"input": input_data})

            if isinstance(input_data, dict) and "input" in input_data and len(input_data)==1:
                payload = input_data["input"]
            else:
                payload = input_data

            prompt = ""
            if isinstance(payload, str):
                prompt = payload
            else:
                prompt = json.dumps(payload, ensure_ascii=False)

            start = time.time()
            response = await agents[agent_name].run(prompt)
            duration = time.time() - start
            response_str = ""
            if not isinstance(response, str):
                try:
                    response_str = json.dumps(response)
                except:
                    response_str= str(response)
            else:
                response_str = response
            if(response_str == "") :
                print("!! No response from agent")
                exit()
            
            # Update the conteyt store
            self.store.update_step_result(step_id, {"output": response_str, "duration": duration}, "success")
            results.append({"step": idx, "agent": agent_name, "status": "success", "output": response_str})
        aggregated = "\n\n".join(r.get("output", r.get("error", "")) for r in results)
        return {"plan_id": planID, "results": results, "aggregated": aggregated}