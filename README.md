# Collaborative Multi-Agent Framework using Model Context Protocol with AI Models

## Problem Statement:
Modern Generative AI systems are being built around certain specialties and optimized for specific types of tasks such as general reasoning, image, sound or other types of media generation and manipulation, code generation or fine-tuned local models. This introduces a need for collaboration of multiple AI agents to achieve a complex task which consists for multiple types of subtasks. Most of the existing systems are often tied to a single provider, restricting the interoperability between multiple agents.

## Proposed Solution:
This project proposes and demonstrates a multi-agent collaboration framework built on Model Context Protocol that enables seamless communication between multiple agents optimized for different purposes. This system introduces an MCP Relay Hub to coordinate message routing and context exchange among different AI agents.

## Expected Outcome:
The project will result in a hybrid multi-agent MCP framework capable of orchestrating tasks across multiple AI agents regardless of their underlying model architecture or hosting environment, demonstrating interoperability, efficiency and context-sharing.

## Project structure
```
llm-mcp-orchestrator/
│
├── README.md   
├── requirements.txt               # Python dependencies
│
├── agents/                        # AI agent implementations
│   ├── __init__.py
│   ├── planner_agent.py          
│   ├── executor_agent.py        
│   ├── cerebras_agent.py        
│   ├── groq_agent.py            
│   ├── local_llm_agent.py       
│   └── gemini_agent.py          
│
├── llm_clients/                   # Low-level LLM API clients
│   ├── cerebras_client.py       
│   ├── groq_client.py           
│   └── local_llm_client.py      
│
├── hub/                           # MCP relay hub
│   ├── __init__.py
│   ├── __main__.py               
│   ├── hub_server.py             # MCP server 
│   └── context_store.py          
│
├── client/                        # Client implementations
│   ├── __init__.py
│   └── cli_client.py             
│
├── results/                       # Sample outputs
│   └── sample_result.txt
```

## Running the project
### Prerequisites
1. Python
2. API keys for Cerebras and Groq
3. Locally installed Ollama

### Commands
1. Create virtual env
```bash
python3 -m venv venv
source venv/bin/activate 
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set environment variables
```bash
export CEREBRAS_API_KEY="cerebras_api_key"
export GROQ_API_KEY="groq_api_key"
```

4. Run the client
```bash
python3 client/cli_client.py "Task description"
```
