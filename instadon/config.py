import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "mastodon": {
        "accounts": {
            "kulturneubau@neubau.social": {
                "instance": "https://neubau.social",
                "access_token": os.getenv("KULTURNEUBAU_MASTODON_ACCESS_TOKEN")
            },
            "dieterkomendera@neubau.social": {
                "instance": "https://neubau.social",
                "access_token": os.getenv("DIETERKOMENDERA_MASTODON_ACCESS_TOKEN")
            },
            "GrueneNeubau@neubau.social": {
                "instance": "https://neubau.social",
                "access_token": os.getenv("GRUENENEUBAU_MASTODON_ACCESS_TOKEN")
            },
            "kaffemik@neubau.social": {
                "instance": "https://neubau.social",
                "access_token": os.getenv("KAFFEMIK_MASTODON_ACCESS_TOKEN")
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
