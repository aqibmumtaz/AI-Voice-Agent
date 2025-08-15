from dataclasses import dataclass, asdict


@dataclass
class Agent:
    agent_name: str = "Ava"
    allow_user_dtmf: bool = True
    language: str = "en-US"
    webhook_url: str = ""
    # Add more default fields as needed

    def __init__(
        self,
        agent_name: str = None,
        allow_user_dtmf: bool = None,
        language: str = None,
        webhook_url: str = None,
        **kwargs
    ):
        if agent_name is not None:
            self.agent_name = agent_name
        if allow_user_dtmf is not None:
            self.allow_user_dtmf = allow_user_dtmf
        if language is not None:
            self.language = language
        if webhook_url is not None:
            self.webhook_url = webhook_url

        # Set any additional fields from kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_dict(self):
        # Remove empty values
        return {k: v for k, v in asdict(self).items() if v not in (None, "")}
