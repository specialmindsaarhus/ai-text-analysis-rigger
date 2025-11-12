import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """
    Konfiguration for applikationen.
    Alle indstillinger kan ændres her eller via .env fil.
    """

    # LLM Provider
    # Vælg mellem: "claude" eller "openai"
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "claude")

    # API Keys
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # Models
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

    # Gradio Settings
    GRADIO_SHARE = os.getenv("GRADIO_SHARE", "false").lower() == "true"
    GRADIO_SERVER_NAME = os.getenv("GRADIO_SERVER_NAME", "127.0.0.1")
    GRADIO_SERVER_PORT = int(os.getenv("GRADIO_SERVER_PORT", "7860"))

    # Standard analyse parametre
    DEFAULT_PARAMETERS = {
        "grammatik": True,
        "stavning": True,
        "struktur": True,
        "klarhed": True
    }

    @classmethod
    def get_api_key(cls):
        """Hent API key baseret på valgt provider"""
        if cls.LLM_PROVIDER == "claude":
            return cls.CLAUDE_API_KEY
        elif cls.LLM_PROVIDER == "openai":
            return cls.OPENAI_API_KEY
        else:
            raise ValueError(f"Ukendt LLM provider: {cls.LLM_PROVIDER}")

    @classmethod
    def get_model(cls):
        """Hent model navn baseret på valgt provider"""
        if cls.LLM_PROVIDER == "claude":
            return cls.CLAUDE_MODEL
        elif cls.LLM_PROVIDER == "openai":
            return cls.OPENAI_MODEL
        else:
            raise ValueError(f"Ukendt LLM provider: {cls.LLM_PROVIDER}")

    @classmethod
    def validate(cls):
        """Valider at nødvendige konfigurationer er sat"""
        api_key = cls.get_api_key()
        if not api_key:
            raise ValueError(
                f"API nøgle ikke sat for {cls.LLM_PROVIDER}. "
                f"Tilføj den til .env filen."
            )
        return True
