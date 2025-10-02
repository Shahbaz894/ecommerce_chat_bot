import os
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# # Load YAML configuration backend\config\configuration.yaml
# ======================
# 📂 Load YAML configuration (backend/config/configuration.yaml)
# ======================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "configuration.yaml")

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)
# ======================
# 📂 Data Sources
# ======================
CSV_FILE_PATH = config.get("data_sources", {}).get("csv_path")
API_URL = config.get("data_sources", {}).get("api_url")

# ======================
# 🔎 Vectorstore
# ======================
VECTORSTORE_CONFIG = config.get("vectorstore", {})

# ======================
# 🧠 Embeddings
# ======================
EMBEDDINGS_CONFIG = config.get("embeddings", {})

# ======================
# 🤖 LLMs
# ======================
LLM_CONFIG = config.get("llm", {})

# def get_llm_config(provider: str = "groq"):
#     """Return the LLM config for a specific provider (openai/groq)."""
#     return LLM_CONFIG.get(provider, {})
import yaml
import os

# Load YAML configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_llm_config(provider: str = "groq") -> dict:
    """
    Return the LLM config for a specific provider from configuration.yaml.
    It also resolves the API key from environment variables.

    Args:
        provider (str): "groq" or "openai"

    Returns:
        dict: Full config including actual API key if available
    """
    llm_cfg = LLM_CONFIG.get(provider, {})

    # Replace API key placeholder with actual value from env vars
    api_key_env = llm_cfg.get("api_key_env")
    if api_key_env:
        llm_cfg["api_key"] = os.getenv(api_key_env, "")

    return llm_cfg

  


# ======================
# 🔐 Secrets from .env
# ======================
ASTRA_DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_DB_KEYSPACE = os.getenv("ASTRA_DB_KEYSPACE", "default_keyspace")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HUGGINGFACEHUB_API_TOKEN = os.getenv("HF_TOKEN")
