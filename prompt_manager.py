from configs import Configs


class PromptManager:
    def __init__(
        self,
        company_name,
        agent_name,
        customer_name,
        due_date,
        service_name,
        balance,
        current_date_time,
    ):
        self.company_name = company_name
        self.agent_name = agent_name
        self.customer_name = customer_name
        self.due_date = due_date
        self.service_name = service_name
        self.balance = balance
        self.current_date_time = current_date_time

    def get_prompt(self):
        return (
            f"You are {self.agent_name}, a virtual agent for a company called {self.company_name}. "
            f"Current date-time is {self.current_date_time}. "
            f"Your job is to notify the user about their pending invoice, which refers to an outstanding payment the user is required to make for services or products rendered by {self.company_name}. "
            f"You are speaking with {self.customer_name}, whose invoice has a due-date of {self.due_date} for the service {self.service_name}. "
            f"Start by introducing yourself as virtual agent and addressing the user by their first name. "
            f"Politely ask if it is a good time to talk, and wait for their response. "
            f"If the user indicates they are unavailable, ask for a date and time to reschedule, and pass these to the reschedule_call function. "
            f"If the user confirms, explain the purpose of the call: to notify them of a pending invoice and ask for a payment date. "
            f"If a payment date is provided, pass it to the inform_invoice function. "
            f"If the user disputes, pass their response to the dispute function. "
            f"If the user says they have already paid, pass their response to the invoice_paid function. "
            f"Keep responses polite, concise, and professional."
        )

    def get_tools(self):
        base_url = Configs.BASE_URL.rstrip("/")
        return [
            {
                "type": "custom",
                "name": "reschedule_call",
                "description": "Reschedules a call for a pending invoice. Requires date and time.",
                "tool_id": "tool_reschedule_call",
                "url": f"{base_url}/reschedule",
                "method": "POST",
            },
            {
                "type": "custom",
                "name": "inform_invoice",
                "description": "Inform the user about their pending invoice and ask for payment date.",
                "tool_id": "tool_inform_invoice",
                "url": f"{base_url}/inform_invoice",
                "method": "POST",
            },
            {
                "type": "custom",
                "name": "dispute",
                "description": "Handle user disputes about the invoice.",
                "tool_id": "tool_dispute",
                "url": f"{base_url}/dispute",
                "method": "POST",
            },
            {
                "type": "custom",
                "name": "invoice_paid",
                "description": "Handle user confirmation of invoice payment.",
                "tool_id": "tool_invoice_paid",
                "url": f"{base_url}/invoice_paid",
                "method": "POST",
            },
        ]
