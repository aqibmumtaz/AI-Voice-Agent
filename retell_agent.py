from configs import Configs
from datetime import datetime
import requests
from prompt_manager import PromptManager


class RetellAgent:
    BASE_URL = "https://api.retellai.com"

    def __init__(self):
        self.api_key = Configs.RETELL_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def create_agent(self):
        url = f"{self.BASE_URL}/create-agent"
        payload = {
            "agent_name": Configs.AGENT_NAME,
            "response_engine": {"llm_id": Configs.LLM_ID, "type": "retell-llm"},
            "voice_id": Configs.VOICE_ID,
        }
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def run_agent(self, agent_id, input_text):
        url = f"{self.BASE_URL}/agents/{agent_id}/run"
        payload = {"input": input_text}
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def list_agents(self):
        url = f"{self.BASE_URL}/agents"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_agent_by_name(self, agent_name):
        agents = self.list_agents()
        for agent in agents:
            if agent.get("name") == agent_name:
                return agent
        return None

    def get_agent_by_name(self, agent_name):
        url = f"{self.BASE_URL}/agents"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        agents = response.json()
        for agent in agents:
            if agent.get("name") == agent_name:
                return agent
        return None


if __name__ == "__main__":
    company_name = "Bitlojix"
    agent_name = "Ava"
    customer_name = "John Doe"
    due_date = "2025-09-01"
    service_name = "Web Hosting"
    balance = "150.00"
    current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    prompt_manager = PromptManager(
        company_name,
        agent_name,
        customer_name,
        due_date,
        service_name,
        balance,
        current_date_time,
    )
    prompt = prompt_manager.get_prompt()
    tools = prompt_manager.get_tools()

    agent_api = RetellAgent()
    agent_name_api = "AI Virtual Agent"
    try:
        existing = agent_api.get_agent_by_name(agent_name_api)
        if existing:
            print(f"Agent '{agent_name_api}' already exists:", existing)
        else:
            result = agent_api.create_invoice_agent(
                prompt, tools, agent_name=agent_name_api
            )
            print("Agent created:", result)
    except Exception as e:
        print("Error creating or fetching agent:", e)
