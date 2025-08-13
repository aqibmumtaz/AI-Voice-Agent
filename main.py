from retell_agent import RetellAgent
from prompt_manager import PromptManager
from retell_agent import RetellAgent

if __name__ == "__main__":
    agent_api = RetellAgent()
    try:
        result = agent_api.create_agent()
        print("Agent created:", result)
    except Exception as e:
        print("Error creating agent:", e)
