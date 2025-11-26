from agents.cerebras_agent import CerebrasAgent
from agents.local_llm_agent import LocalLLMGeneratedAgent
import re
import json

planner_prompt_base = "You are a planning assistant. Return JSON only with the key 'plan' mapping to a list of steps. "
"Each step should have: step_index (int), action (summarize|generate_code|explain_code|test_code|refine), agent (cerebras|groq|local), input (string or object).\n\n"
"Agent selection guidelines:\n"
"- Use 'groq' for: code generation, programming tasks, fast inference\n"
"- Use 'cerebras' for: complex analysis, detailed explanations, long-form reasoning\n"
"- Use 'local' for: simple questions, basic text tasks, quick summaries, formatting\n\n"
"Distribute tasks across multiple agents when appropriate. Use local agent for simple steps. Break complex requests into multiple steps using different specialized agents.\n\n"
"User request:\n"

class PlannerAgent:
    def __init__(self, cerebras_model="llama3.1-8b", local_model="llama3:latest"):
        self.cerebras = CerebrasAgent(model=cerebras_model)
        self.local = LocalLLMGeneratedAgent(model=local_model)

    async def plan(self, prompt):
        prompt = planner_prompt_base + prompt
        print("----------")
        print("Planning Agent preparing plan...")
        plann = await self.cerebras.run(prompt)

        # get the json
        if not isinstance(plann, str):
            plann = str(plann)
        plann = plann.strip()
        plann = re.sub(r"```(?:json)?\n", "", plann, flags=re.IGNORECASE)
        m= re.search(r"\{.*\}", plann, flags=re.DOTALL)
        if m:
            plann = m.group(0)
        else:
            m = re.search(r"\[.*\]", plann, flags=re.DOTALL)
            if m:
                plann = json.dumps({"plan": json.loads(m.group(0))})

        parsed_plan = json.loads(plann)
        if "plan" not in parsed_plan or not isinstance(parsed_plan["plan"], list):
            print("!! Plan invalid. Exiting.")
            exit()

        print("-----------")
        print("Refine plan with local agent")
        refining_prompt = "Refine this plan to be more reliable. Return JSON only:\n\n" + json.dumps(parsed_plan)
        new_prompt = await self.local.run(refining_prompt)
        new_prompt_json = ""
        if not isinstance(new_prompt, str):
            new_prompt_json = str(new_prompt)
        new_prompt_json = new_prompt_json.strip()
        new_prompt_json = re.sub(r"```(?:json)?\n", "", new_prompt_json, flags=re.IGNORECASE)
        m= re.search(r"\{.*\}", new_prompt_json, flags=re.DOTALL)
        if m:
            new_prompt_json = m.group(0)
        else:
            m = re.search(r"\[.*\]", new_prompt_json, flags=re.DOTALL)
            if m:
                new_prompt_json = json.dumps({"plan": json.loads(m.group(0))})
        
        if new_prompt_json:
            new_prompt_obj = json.loads(new_prompt_json)
            if "plan" in new_prompt_obj and isinstance(new_prompt_obj["plan"], list):
                return new_prompt_obj
            else:
                print("!! Refined plan invalid. Exiting.")
                exit()

