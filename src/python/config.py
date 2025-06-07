import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "mastodon": {
        "instance": os.getenv("MASTODON_INSTANCE", "https://neubau.social"),
        "access_token": os.getenv("MASTODON_ACCESS_TOKEN", "czPVtqZUvT5RvxTE_KVygunCiupXxre-71SBIndYf_o")
    },
    "cobalt": {
        "url": "https://cobalt.uber.space/"
    },
    "openrouter": {
        "api_key": os.getenv("OPENROUTER_API_KEY", "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"),
        "base_url": "https://openrouter.ai/api/v1",
        "model": "deepseek/deepseek-chat-v3-0324:free"
    }
}
