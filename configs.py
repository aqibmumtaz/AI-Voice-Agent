import os
from dotenv import load_dotenv


class Configs:
    """
    Configs class loads .env variables and provides class-level access.
    Usage: Configs.load_configs(); then access variables as Configs.RETELL_API_KEY
    """

    RETELL_API_KEY = None
    LLM_ID = None
    VOICE_ID = None
    RETELL_AGENT_NAME = None

    _TYPES = {
        "RETELL_API_KEY": str,
        "LLM_ID": str,
        "VOICE_ID": str,
        "RETELL_AGENT_NAME": str,
        # "MAX_CALLS": int,
        # "THRESHOLD": float,
        # "DEBUG_MODE": bool,
    }

    @classmethod
    def _convert_type(cls, value, target_type):
        if value is None:
            return None
        try:
            if target_type == int:
                return int(value)
            elif target_type == float:
                return float(value)
            elif target_type == bool:
                return value.lower() in ("true", "1", "yes")
            else:
                return value
        except Exception:
            return value

    @classmethod
    def load_configs(cls):
        load_dotenv()
        for key, typ in cls._TYPES.items():
            val = os.getenv(key)
            setattr(cls, key, cls._convert_type(val, typ))

    # Utility function to print all config variables for debugging
    def print_all_configs():
        print("\n****************** Configs ******************")
        for attr in dir(Configs):
            if (
                not attr.startswith("__")
                and not callable(getattr(Configs, attr))
                and attr != "_TYPES"
            ):
                print(f"{attr}: {getattr(Configs, attr)}")
        print("--- End Configs ---")


# Ensure configs are loaded on import
Configs.load_configs()
Configs.print_all_configs()
