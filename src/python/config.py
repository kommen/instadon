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
    }
}
