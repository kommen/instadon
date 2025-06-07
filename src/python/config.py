import os
from typing import Dict, Any


CONFIG = {
    "mastodon": {
        "instance": os.getenv("MASTODON_INSTANCE", "https://neubau.social"),
        "access_token": os.getenv("MASTODON_ACCESS_TOKEN", "czPVtqZUvT5RvxTE_KVygunCiupXxre-71SBIndYf_o")
    },
    "cobalt": {
        "url": "https://cobalt.uber.space/"
    },
    "openrouter": {
        "api_key": os.getenv("OPENROUTER_API_KEY"),
        "base_url": "https://openrouter.ai/api/v1",
        "model": "deepseek/deepseek-chat-v3-0324:free"
    }
}
