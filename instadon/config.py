import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "mastodon": {
        "accounts": {
            "neubau.social": {
                "instance": os.getenv("MASTODON_INSTANCE"),
                "access_token": os.getenv("MASTODON_ACCESS_TOKEN")
            },
            "wien.rocks": {
                "instance": os.getenv("MASTODON_INSTANCE_2"),
                "access_token": os.getenv("MASTODON_ACCESS_TOKEN_2")
            }
        }
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
