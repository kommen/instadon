import requests
import logging
from typing import List, Optional, Dict, Any
from .config import CONFIG

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MastodonClient:
    def __init__(self, account: str):
        accounts = CONFIG["mastodon"]["accounts"]
        if account not in accounts:
            available_accounts = list(accounts.keys())
            raise ValueError(f"Account '{account}' not found. Available accounts: {available_accounts}")
        
        account_config = accounts[account]
        self.instance = account_config["instance"]
        self.access_token = account_config["access_token"]
        self.account_name = account
        
        if not self.access_token:
            raise ValueError(f"No access token configured for account '{account}'")
        
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }
        
        logger.info(f"Initialized Mastodon client for account '{account}' at {self.instance}")
    
    def upload_media(self, file_path: str, description: str) -> str:
        """Upload media to Mastodon and return media ID."""
        url = f"{self.instance}/api/v2/media"
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'description': description}
            
            response = requests.post(url, headers=self.headers, files=files, data=data)
            response.raise_for_status()
            
            return response.json()['id']
    
    def create_post(self, status: str, media_ids: List[str], visibility: str = "public", in_reply_to_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a post in Mastodon."""
        url = f"{self.instance}/api/v1/statuses"
        
        data = {
            "status": status,
            "media_ids": media_ids,
            "visibility": visibility
        }
        
        if in_reply_to_id:
            data["in_reply_to_id"] = in_reply_to_id
        
        logger.info(f"Creating Mastodon post at: {url}")
        logger.info(f"Request headers: {self.headers}")
        logger.info(f"Request data: {data}")
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            
            if response.status_code != 200:
                logger.error(f"HTTP {response.status_code} error from Mastodon API")
                logger.error(f"Response text: {response.text}")
                
                # Try to parse error details if available
                try:
                    error_data = response.json()
                    logger.error(f"Error details: {error_data}")
                except:
                    logger.error("Could not parse error response as JSON")
            
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Mastodon API response: {result}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Error response text: {e.response.text}")
            raise

    def create_post_thread(self, status: str, media_ids: List[str], visibility: str = "public") -> List[Dict[str, Any]]:
        """Create a thread of posts if media exceeds Mastodon's 4-attachment limit."""
        MAX_MEDIA_PER_POST = 4
        posts = []
        
        if len(media_ids) <= MAX_MEDIA_PER_POST:
            # Single post is sufficient
            post = self.create_post(status, media_ids, visibility)
            posts.append(post)
            return posts
        
        # Split media into chunks of 4
        media_chunks = [media_ids[i:i + MAX_MEDIA_PER_POST] for i in range(0, len(media_ids), MAX_MEDIA_PER_POST)]
        
        logger.info(f"Creating thread with {len(media_chunks)} posts for {len(media_ids)} media files")
        
        # Create first post with original status and visibility
        first_chunk = media_chunks[0]
        first_post = self.create_post(status, first_chunk, visibility)
        posts.append(first_post)
        
        # Create reply posts for remaining media chunks
        reply_to_id = first_post["id"]
        for i, chunk in enumerate(media_chunks[1:], 1):
            # Reply posts are unlisted to avoid spam
            reply_visibility = "unlisted"
            reply_status = f"({i + 1}/{len(media_chunks)})"  # Simple continuation indicator
            
            reply_post = self.create_post(reply_status, chunk, reply_visibility, reply_to_id)
            posts.append(reply_post)
            
            # Next reply should reply to this post to create a chain
            reply_to_id = reply_post["id"]
        
        logger.info(f"Successfully created thread with {len(posts)} posts")
        return posts
