from configs import Configs
from datetime import datetime
from prompt_manager import PromptManager
from retell import Retell


class RetellAgent:
    def __init__(self):
        self.client = Retell(api_key=Configs.RETELL_API_KEY)

    # LLM methods
    def create_llm(self):
        """Create a new Retell LLM and return its llm_id. Updates Configs.LLM_ID."""
        print("Creating a new Retell LLM...")
        llm_response = self.client.llm.create()
        llm_id = llm_response.llm_id
        print(f"Created new LLM with id: {llm_id}")
        Configs.LLM_ID = llm_id
        return llm_id

    def get_llm(self, llm_id=None):
        """Get a Retell LLM by id (or from config if not provided)."""
        if llm_id is None:
            llm_id = Configs.LLM_ID
        return self.client.llm.get(llm_id=llm_id)

    def update_llm(self, llm_id, **kwargs):
        """Update a Retell LLM by id."""
        return self.client.llm.update(llm_id=llm_id, **kwargs)

    def delete_llm(self, llm_id):
        """Delete a Retell LLM by id."""
        return self.client.llm.delete(llm_id=llm_id)

    # Agent methods
    def create_agent(self, response_engine, voice_id, **kwargs):
        return self.client.agent.create(
            response_engine=response_engine, voice_id=voice_id, **kwargs
        )

    def list_agents(self, is_published=True):
        agents = self.client.agent.list()
        if is_published is not None:
            filtered_agents = []
            for a in agents:
                try:
                    if a.is_published == is_published:
                        filtered_agents.append(a)
                except AttributeError:
                    pass
            agents = filtered_agents
        return agents

    def get_agent(self, agent_id):
        return self.client.agent.get(agent_id=agent_id)

    def update_agent(self, agent_id, **kwargs):
        return self.client.agent.update(agent_id=agent_id, **kwargs)

    def delete_agent(self, agent_id):
        return self.client.agent.delete(agent_id=agent_id)

    def get_agent_by_name(self, agent_name, is_published=True):
        agents = self.list_agents(is_published=is_published)
        for agent in agents:
            try:
                if agent.agent_name == agent_name:
                    return agent
            except AttributeError:
                pass
        return None

    def run_agent(self, agent_id, input_text):
        # The SDK may have a different method for running an agent; adjust as needed
        return self.client.agent.run(agent_id=agent_id, input=input_text)


def init_agent():
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
    agent_name = Configs.AGENT_NAME
    try:
        existing = agent_api.get_agent_by_name(agent_name)
        if existing:
            print(f"Agent '{agent_name}' already exists:", existing)
        else:
            llm_id = agent_api.create_llm()
            response_engine = {"llm_id": llm_id, "type": "retell-llm"}
            print(f"Using response_engine: {response_engine}")
            print(f"Using voice_id: {Configs.VOICE_ID}")
            result = agent_api.create_agent(
                response_engine=response_engine, voice_id=Configs.VOICE_ID
            )
            print("Agent created:", result)
    except Exception as e:
        print("Error creating or fetching agent:", e)


if __name__ == "__main__":
    init_agent()
