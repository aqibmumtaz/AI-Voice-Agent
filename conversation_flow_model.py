from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


@dataclass
class ConversationFlow:
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    start_node_id: str = "start"
    start_speaker: str = "agent"
    model_choice: Dict[str, Any] = field(
        default_factory=lambda: {"model": "gpt-4o-mini", "type": "cascading"}
    )
    global_prompt: Optional[str] = None
    tools: Optional[List[Dict[str, Any]]] = field(default_factory=list)
    model_temperature: Optional[float] = None
    tool_call_strict_mode: Optional[bool] = None
    default_dynamic_variables: Optional[Dict[str, Any]] = None
    knowledge_base_ids: Optional[List[str]] = None
    begin_tag_display_position: Optional[Dict[str, int]] = None
    mcps: Optional[List[Dict[str, Any]]] = None
    # Add more fields as needed

    def __init__(
        self,
        nodes: List[Dict[str, Any]] = None,
        start_node_id: str = None,
        start_speaker: str = None,
        model_choice: Dict[str, Any] = None,
        global_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        model_temperature: Optional[float] = None,
        tool_call_strict_mode: Optional[bool] = None,
        default_dynamic_variables: Optional[Dict[str, Any]] = None,
        knowledge_base_ids: Optional[List[str]] = None,
        begin_tag_display_position: Optional[Dict[str, int]] = None,
        mcps: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ):
        # Set defaults
        self.nodes = nodes if nodes is not None else []
        self.start_node_id = start_node_id if start_node_id is not None else "start"
        self.start_speaker = start_speaker if start_speaker is not None else "agent"
        self.model_choice = (
            model_choice
            if model_choice is not None
            else {"model": "gpt-4o-mini", "type": "cascading"}
        )
        self.global_prompt = global_prompt
        # Ensure tools is always a list
        if tools is None:
            self.tools = []
        else:
            if not isinstance(tools, list):
                raise ValueError("tools must be a list of dicts")
            for tool in tools:
                if not isinstance(tool, dict):
                    raise ValueError("Each tool must be a dict")
            self.tools = tools
        self.model_temperature = model_temperature
        self.tool_call_strict_mode = tool_call_strict_mode
        self.default_dynamic_variables = default_dynamic_variables
        self.knowledge_base_ids = knowledge_base_ids
        self.begin_tag_display_position = begin_tag_display_position
        self.mcps = mcps
        # Set any additional fields from kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_dict(self):
        d = asdict(self)
        # Remove None values for clean payload
        return {k: v for k, v in d.items() if v is not None}

    @staticmethod
    def single_prompt_flow(prompt, tools=None, **kwargs):
        nodes = [
            {
                "id": kwargs.get("start_node_id", "start"),
                "instruction": {
                    "text": prompt,
                    "type": "prompt",
                },
                "type": "conversation",
            }
        ]
        # Set model_choice and start_speaker as in doc example unless overridden
        model_choice = kwargs.pop(
            "model_choice", {"model": "gpt-4o-mini", "type": "cascading"}
        )
        start_speaker = kwargs.pop("start_speaker", "agent")
        return ConversationFlow(
            nodes=nodes,
            model_choice=model_choice,
            start_speaker=start_speaker,
            tools=tools,
            **kwargs
        )
