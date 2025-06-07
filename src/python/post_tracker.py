import logging
from pathlib import Path
from typing import Set

logger = logging.getLogger(__name__)

class PostTracker:
    def __init__(self, tracker_file: str = "posted_instagram_ids.txt"):
        self.tracker_file = Path(tracker_file)
        self._ensure_tracker_file_exists()
    
    def _ensure_tracker_file_exists(self):
        """Create tracker file if it doesn't exist."""
        if not self.tracker_file.exists():
            self.tracker_file.touch()
            logger.info(f"Created new post tracker file: {self.tracker_file}")
    
    def is_already_posted(self, shortcode: str) -> bool:
        """Check if an Instagram post has already been posted to Mastodon."""
        try:
            with open(self.tracker_file, 'r') as f:
                posted_ids = {line.strip() for line in f if line.strip()}
            
            is_posted = shortcode in posted_ids
            logger.info(f"Post {shortcode} already posted: {is_posted}")
            return is_posted
            
        except Exception as e:
            logger.error(f"Error reading tracker file: {e}")
            return False
    
    def mark_as_posted(self, shortcode: str):
        """Mark an Instagram post as posted to Mastodon."""
        try:
            # Check if already exists to avoid duplicates
            if not self.is_already_posted(shortcode):
                with open(self.tracker_file, 'a') as f:
                    f.write(f"{shortcode}\n")
                logger.info(f"Marked post {shortcode} as posted")
            else:
                logger.info(f"Post {shortcode} already marked as posted")
                
        except Exception as e:
            logger.error(f"Error writing to tracker file: {e}")
