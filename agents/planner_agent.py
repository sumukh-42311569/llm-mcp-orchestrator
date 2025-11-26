from agents.cerebras_agent import CerebrasAgent
from agents.local_llm_agent import LocalLLMGeneratedAgent
import re
import json

planner_prompt_base = """You are a task planning assistant. Your job is to break down a user's request into a structured execution plan with multiple steps using different specialized agents.

IMPORTANT: Return ONLY a JSON object. Do not write code. Do not explain. Just return pure JSON.

The JSON must have this exact structure:
{
  "plan": [
    {
      "step_index": 1,
      "action": "summarize",
      "agent": "local",
      "input": "description of what to summarize or analyze"
    },
    {
      "step_index": 2,
      "action": "generate_code",
      "agent": "groq",
      "input": "description of what code to generate"
    },
    {
      "step_index": 3,
      "action": "explain_code",
      "agent": "cerebras",
      "input": "what code to explain in detail"
    }
  ]
}

Valid actions: summarize, generate_code, explain_code, test_code, refine
Valid agents and their specialties:
- local: Simple tasks, quick summaries, requirements analysis, task decomposition, formatting, simple text processing
- groq: Code generation, programming tasks, fast inference, technical implementations
- cerebras: Complex analysis, detailed explanations, long-form reasoning, in-depth reviews

CRITICAL RULES:
1. ALWAYS break tasks into AT LEAST 2-3 steps
2. ALWAYS use the 'local' agent for initial analysis, summarization, or requirement gathering
3. Use different agents for different steps to distribute the workload
4. For code-related tasks, follow this pattern:
   - Step 1: Use 'local' to analyze requirements or create a task breakdown
   - Step 2: Use 'groq' to generate the actual code
   - Step 3: Use 'cerebras' or 'local' to review, explain, or validate

User request:
"""

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
        
        # Save raw response for debugging
        import os
        debug_file = os.path.join(os.path.dirname(__file__), "..", "data", "debug_response.txt")
        with open(debug_file, "w") as f:
            f.write(f"Raw response:\n{plann}\n\n")
        
        print(f"Raw response from Cerebras (first 500 chars): {plann[:500]}")
        
        # Remove markdown code blocks
        plann = re.sub(r"```(?:json)?\n?", "", plann, flags=re.IGNORECASE)
        plann = re.sub(r"```\n?$", "", plann, flags=re.IGNORECASE)
        plann = plann.strip()
        
        # Look for JSON in **Output:** section if it exists
        output_match = re.search(r'\*\*Output:\*\*\s*({.*?})', plann, flags=re.DOTALL)
        if output_match:
            plann = output_match.group(1)
            print("Found JSON in Output section")
        
        # Try to extract JSON object - look for properly formatted JSON with double quotes
        m = re.search(r'(\{[\s\S]*?"plan"[\s\S]*?\[[\s\S]*?\][\s\S]*?\})', plann)
        if m:
            plann = m.group(1)
        else:
            # Fall back to finding any JSON object
            m = re.search(r"\{.*\}", plann, flags=re.DOTALL)
            if m:
                plann = m.group(0)
            else:
                m = re.search(r"\[.*\]", plann, flags=re.DOTALL)
                if m:
                    plann = json.dumps({"plan": json.loads(m.group(0))})
        
        # Fix common JSON issues: single quotes to double quotes
        # But be careful not to break strings that contain apostrophes
        plann = plann.replace("'", '"')
        
        print(f"Extracted JSON (first 500 chars): {plann[:500]}")
        
        # Save extracted JSON for debugging
        with open(debug_file, "a") as f:
            f.write(f"Extracted JSON:\n{plann}\n\n")

        try:
            parsed_plan = json.loads(plann)
        except json.JSONDecodeError as e:
            print(f"!! JSON decode error: {e}")
            print(f"!! Failed to parse (first 200 chars): {plann[:200]}")
            with open(debug_file, "a") as f:
                f.write(f"ERROR: {e}\n")
            raise ValueError(f"Failed to parse plan JSON: {e}. Check {debug_file} for details")
        if "plan" not in parsed_plan or not isinstance(parsed_plan["plan"], list):
            print("!! Plan invalid.")
            raise ValueError("Invalid plan structure: missing 'plan' key or not a list")

        print("-----------")
        print("Refine plan with local agent")
        
        # Try to refine with local agent, but don't fail if it's not available
        try:
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
                    print("Plan successfully refined by local agent")
                    return new_prompt_obj
                else:
                    print("!! Refined plan invalid. Returning original plan.")
                    return parsed_plan
            else:
                print("!! No refined plan generated. Returning original plan.")
                return parsed_plan
        except Exception as e:
            print(f"!! Local agent refinement failed: {e}")
            print("!! Returning original plan without refinement.")
            return parsed_plan

