import requests
from typing import List, Optional, Dict, Any
from .config import CONFIG

class MastodonClient:
    def __init__(self):
        self.instance = CONFIG["mastodon"]["instance"]
        self.access_token = CONFIG["mastodon"]["access_token"]
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }
    
    def upload_media(self, file_path: str, description: str) -> str:
        """Upload media to Mastodon and return media ID."""
        url = f"{self.instance}/api/v2/media"
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'description': description}
            
            response = requests.post(url, headers=self.headers, files=files, data=data)
            response.raise_for_status()
            
            return response.json()['id']
    
    def create_draft(self, status: str, media_ids: List[str], visibility: str = "public") -> Dict[str, Any]:
        """Create a draft post in Mastodon."""
        url = f"{self.instance}/api/v1/statuses"
        
        data = {
            "status": status,
            "media_ids": media_ids,
            "visibility": visibility,
            "draft": True
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        
        return response.json()
