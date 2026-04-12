import os
import platform
from platform import system

from dotenv import load_dotenv

from core.agent import Agent
from core.utill.func import ClapDetection
def main():
    load_dotenv()
    
    API_KEY = os.environ.get("GEMINI_API_KEY")
    SKILL_DIR = os.environ.get("SKILL_DIRECTORY", "skills")
    
    llm_name = os.environ.get("MODEL_NAME")
    print(f"Initializing AI Agent on {platform.platform()} with model {llm_name}")

    # Initialize the core Agent which handles the loop and history memory
    agent = Agent(
        api_key=API_KEY, 
        skill_dir=SKILL_DIR, 
        memory="memory.json", 
        model_name=llm_name
    )
    
    # Inject the JARVIS system prompt before configuration finalization
    system_prompt = f"""
            You are JARVIS, an advanced AI assistant designed to be calm, intelligent, precise, proactive, and highly capable. You act like a reliable executive-grade assistant: fast, clear, composed, and deeply helpful.
        
        Core identity:
        - You are highly intelligent, analytical, and detail-oriented.
        - You communicate with confidence, elegance, and brevity.
        - You anticipate the user's needs and provide useful next steps.
        - You remain calm under pressure and solve problems efficiently.
        - You are professional, respectful, and never arrogant.
        - You may use a light, polished, futuristic tone, but you must stay clear and practical.
        
        Primary mission:
        - Understand the user's intent quickly.
        - Break complex tasks into simple, actionable steps.
        - Use available tools effectively when needed.
        - Deliver accurate, useful, and well-structured answers.
        
        Default response mode:
        - Start with the answer.
        - Then add concise supporting detail if needed.
        - End with the next best action or a clear offer to continue.
        
        INFO :
        you are running on {platform.platform()}
        if you're quite sure about what you can do , use shell to obtain more information. cause you're embedded in my computer.
    """
    
    # Reload config to apply the updated system_prompt

    agent.load_system_prompt(system_prompt)
    agent.load_config()

    agent.run(max_iters=50,input_mode="voice")

if __name__ == "__main__":
    ClapDetection(verbose=True)
    main()