from dataclasses import dataclass, asdict


@dataclass
class Agent:
    agent_name: str = "Ava"
    prompt: str = ""
    voice_model: str = "eleven_turbo_v2"
    voice_temperature: float = 1.0
    voice_speed: float = 1.0
    volume: float = 1.0
    responsiveness: float = 1.0
    interruption_sensitivity: float = 1.0
    enable_backchannel: bool = False
    backchannel_frequency: float = 0.0
    backchannel_words: list = None
    reminder_trigger_ms: int = 10000
    reminder_max_count: int = 0
    ambient_sound: str = ""
    ambient_sound_volume: float = 1.0
    language: str = "en-US"
    webhook_url: str = ""
    description: str = ""
    boosted_keywords: list = None
    tools: list = None
    opt_out_sensitive_data_storage: bool = False
    opt_in_signed_url: bool = False
    pronunciation_dictionary: list = None
    normalize_for_speech: bool = True
    end_call_after_silence_ms: int = 35000
    max_call_duration_ms: int = 300000
    voicemail_option: dict = None
    post_call_analysis_data: list = None
    post_call_analysis_model: str = None
    begin_message_delay_ms: int = 0
    ring_duration_ms: int = 30000
    stt_mode: str = "fast"
    vocab_specialization: str = "general"
    allow_user_dtmf: bool = True
    user_dtmf_options: dict = None
    denoising_mode: str = ""
    is_published: bool = False
    call_settings: dict = None
    last_modification_timestamp: int = None
    # Reference fields that point to other objects: keep at end in this order
    voice_id: str = ""
    fallback_voice_ids: list = None
    knowledge_base_id: str = ""
    conversation_flow_id: str = ""

    def __init__(
        self,
        agent_name: str = None,
        prompt: str = None,
        voice_model: str = None,
        voice_temperature: float = None,
        voice_speed: float = None,
        volume: float = None,
        responsiveness: float = None,
        interruption_sensitivity: float = None,
        enable_backchannel: bool = None,
        backchannel_frequency: float = None,
        backchannel_words: list = None,
        reminder_trigger_ms: int = None,
        reminder_max_count: int = None,
        ambient_sound: str = None,
        ambient_sound_volume: float = None,
        language: str = None,
        webhook_url: str = None,
        description: str = None,
        boosted_keywords: list = None,
        tools: list = None,
        opt_out_sensitive_data_storage: bool = None,
        opt_in_signed_url: bool = None,
        pronunciation_dictionary: list = None,
        normalize_for_speech: bool = None,
        end_call_after_silence_ms: int = None,
        max_call_duration_ms: int = None,
        voicemail_option: dict = None,
        post_call_analysis_data: list = None,
        post_call_analysis_model: str = None,
        begin_message_delay_ms: int = None,
        ring_duration_ms: int = None,
        stt_mode: str = None,
        vocab_specialization: str = None,
        allow_user_dtmf: bool = None,
        user_dtmf_options: dict = None,
        denoising_mode: str = None,
        is_published: bool = None,
        call_settings: dict = None,
        last_modification_timestamp: int = None,
        voice_id: str = None,
        fallback_voice_ids: list = None,
        knowledge_base_id: str = None,
        conversation_flow_id: str = None,
        **kwargs
    ):
        if agent_name is not None:
            self.agent_name = agent_name
        if prompt is not None:
            self.prompt = prompt
        if voice_model is not None:
            self.voice_model = voice_model
        # Ensure voice_model is always a valid TTS model
        allowed_voice_models = [
            "eleven_turbo_v2",
            "eleven_flash_v2",
            "eleven_turbo_v2_5",
            "eleven_flash_v2_5",
            "eleven_multilingual_v2",
            "sonic-2",
            "sonic-turbo",
            "tts-1",
            "gpt-4o-mini-tts",
        ]
        if getattr(self, "voice_model", None) not in allowed_voice_models:
            self.voice_model = "eleven_turbo_v2"
        if voice_temperature is not None:
            self.voice_temperature = voice_temperature
        if voice_speed is not None:
            self.voice_speed = voice_speed
        if volume is not None:
            self.volume = volume
        if responsiveness is not None:
            self.responsiveness = responsiveness
        if interruption_sensitivity is not None:
            self.interruption_sensitivity = interruption_sensitivity
        if enable_backchannel is not None:
            self.enable_backchannel = enable_backchannel
        if backchannel_frequency is not None:
            self.backchannel_frequency = backchannel_frequency
        if backchannel_words is not None:
            self.backchannel_words = backchannel_words
        if reminder_trigger_ms is not None:
            self.reminder_trigger_ms = reminder_trigger_ms
        if reminder_max_count is not None:
            self.reminder_max_count = reminder_max_count
        if ambient_sound is not None:
            self.ambient_sound = ambient_sound
        if ambient_sound_volume is not None:
            self.ambient_sound_volume = ambient_sound_volume
        if language is not None:
            self.language = language
        if webhook_url is not None:
            self.webhook_url = webhook_url
        if description is not None:
            self.description = description
        if boosted_keywords is not None:
            self.boosted_keywords = boosted_keywords
        if tools is not None:
            self.tools = tools
        if opt_out_sensitive_data_storage is not None:
            self.opt_out_sensitive_data_storage = opt_out_sensitive_data_storage
        if opt_in_signed_url is not None:
            self.opt_in_signed_url = opt_in_signed_url
        if pronunciation_dictionary is not None:
            self.pronunciation_dictionary = pronunciation_dictionary
        if normalize_for_speech is not None:
            self.normalize_for_speech = normalize_for_speech
        if end_call_after_silence_ms is not None:
            self.end_call_after_silence_ms = end_call_after_silence_ms
        if max_call_duration_ms is not None:
            self.max_call_duration_ms = max_call_duration_ms
        if voicemail_option is not None:
            self.voicemail_option = voicemail_option
        if post_call_analysis_data is not None:
            self.post_call_analysis_data = post_call_analysis_data
        if post_call_analysis_model is not None:
            self.post_call_analysis_model = post_call_analysis_model
        if begin_message_delay_ms is not None:
            self.begin_message_delay_ms = begin_message_delay_ms
        if ring_duration_ms is not None:
            self.ring_duration_ms = ring_duration_ms
        if stt_mode is not None:
            self.stt_mode = stt_mode
        if vocab_specialization is not None:
            self.vocab_specialization = vocab_specialization
        if allow_user_dtmf is not None:
            self.allow_user_dtmf = allow_user_dtmf
        if user_dtmf_options is not None:
            self.user_dtmf_options = user_dtmf_options
        if denoising_mode is not None:
            self.denoising_mode = denoising_mode
        if is_published is not None:
            self.is_published = is_published
        if call_settings is not None:
            self.call_settings = call_settings
        if last_modification_timestamp is not None:
            self.last_modification_timestamp = last_modification_timestamp
        # Set reference fields at the end
        if voice_id is not None:
            self.voice_id = voice_id
        if fallback_voice_ids is not None:
            self.fallback_voice_ids = fallback_voice_ids
        if knowledge_base_id is not None:
            self.knowledge_base_id = knowledge_base_id
        if conversation_flow_id is not None:
            self.conversation_flow_id = conversation_flow_id

        # Set any additional fields from kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_dict(self):
        # Build payload compatible with Retell SDK: move prompt into a nested `config` dict
        d = asdict(self)
        payload = {}

        # Remove is_published and conversation_flow_id (not accepted by create API)
        d.pop("is_published", None)
        d.pop("conversation_flow_id", None)

        # Extract prompt into config
        prompt_val = d.pop("prompt", None)
        config = {}
        if prompt_val not in (None, ""):
            config["prompt"] = prompt_val

        # Keep other top-level fields, excluding empty values
        for k, v in d.items():
            if v in (None, "", [], {}):
                continue
            payload[k] = v

        # Attach config if it has content
        if config:
            payload["config"] = config

        return payload
