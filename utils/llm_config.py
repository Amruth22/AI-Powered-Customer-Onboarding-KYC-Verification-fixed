import os
import json
from crewai.llm import LLM
from dotenv import load_dotenv
from typing import Optional, Dict, Any

load_dotenv()


def load_config() -> Dict[str, Any]:
    """
    Load application configuration from JSON file.

    Returns:
        Dict containing application configuration
    """
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'configs', 'app_config.json')

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        # Return default config if file doesn't exist
        return {
            "llm_config": {
                "model": "gemini/gemini-2.0-flash",
                "max_tokens": 3000,
                "temperature": 0.0
            }
        }


def get_llm_config(
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None
) -> LLM:
    """
    Get configured LLM instance for CrewAI agents.

    This centralizes LLM configuration to avoid repetition across all agent files.

    Args:
        model: Override the default model from config
        api_key: Override the API key from environment
        max_tokens: Override the max_tokens from config
        temperature: Override the temperature from config

    Returns:
        Configured LLM instance ready to use with CrewAI agents

    Example:
        llm = get_llm_config()
        agent = Agent(role="Test", goal="Test", llm=llm)
    """
    config = load_config()
    llm_config = config.get('llm_config', {})

    final_api_key = api_key or os.getenv('GEMINI_API_KEY')

    if not final_api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    final_model = model or llm_config.get('model', 'gemini/gemini-2.0-flash')
    final_max_tokens = max_tokens or llm_config.get('max_tokens', 3000)
    final_temperature = temperature if temperature is not None else llm_config.get('temperature', 0.0)

    llm = LLM(
        model=final_model,
        api_key=final_api_key,
        max_tokens=final_max_tokens,
        temperature=final_temperature
    )

    return llm


def get_custom_llm_config(custom_settings: Dict[str, Any]) -> LLM:
    """
    Get LLM configuration with custom settings.

    Useful for agents that need specific LLM configurations
    different from the default.

    Args:
        custom_settings: Dictionary with custom LLM settings
            - model: str
            - max_tokens: int
            - temperature: float
            - api_key: str (optional)

    Returns:
        Configured LLM instance with custom settings

    Example:
        custom = {"temperature": 0.7, "max_tokens": 4000}
        llm = get_custom_llm_config(custom)
    """
    return get_llm_config(
        model=custom_settings.get('model'),
        api_key=custom_settings.get('api_key'),
        max_tokens=custom_settings.get('max_tokens'),
        temperature=custom_settings.get('temperature')
    )
