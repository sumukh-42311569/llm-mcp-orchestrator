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
        context_history = []  # Store outputs from previous steps

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
            
            # Add context from previous steps
            if context_history:
                context_text = "\n\n--- Context from previous steps ---\n"
                for i, prev_result in enumerate(context_history, 1):
                    context_text += f"\nStep {i} ({prev_result['agent']}):\n{prev_result['output'][:500]}\n"
                prompt = context_text + "\n--- Your task ---\n" + prompt

            start = time.time()
            response = await agents[agent_name].run(prompt)
            duration = time.time() - start
            
            if not isinstance(response, str):
                response_str = json.dumps(response)
            else:
                response_str = response
                
            if not response_str:
                raise ValueError(f"Empty response from agent {agent_name}")
            
            # Update the context store
            self.store.update_step_result(step_id, {"output": response_str, "duration": duration}, "success")
            
            result = {"step": idx, "agent": agent_name, "status": "success", "output": response_str}
            results.append(result)
            context_history.append(result)  # Add to context for next steps
            
        aggregated = "\n\n".join(r.get("output", r.get("error", "")) for r in results)
        return {"plan_id": planID, "results": results, "aggregated": aggregated}