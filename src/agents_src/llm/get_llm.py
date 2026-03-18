from crewai import LLM
from src.agents_src.config.agent_settings import AgentSettings
from src.agents_src.llm.llm_configuration import LLM_CONFIG

def get_llm_for_agent(agent_name):
    settings = AgentSettings()
    model = LLM_CONFIG.get(agent_name, {}).get("model", "groq/llama-3.3-70b-versatile")
    temperature = LLM_CONFIG.get(agent_name, {}).get("temperature", 0.1)
    
    print(f">>> Using model: {model}")  # ✅ add this to confirm which model is loading
    
    llm = LLM(
        model=model,
        temperature=temperature,
        api_key=settings.GROQ_API_KEY,
    )
    return llm
