import instaloader
from typing import Optional
from datetime import datetime
from pathlib import Path
import re

class InstagramClient:
    def __init__(self, session_file: str = "kommen"):
        self.loader = instaloader.Instaloader()
        
        # Use session_file as the username and generate local path
        username = session_file
        session_path = Path(f"{username}_session")
        
        # Load session with username and local file path
        self.loader.load_session_from_file(username, str(session_path))
    
    def latest_post(self, profile_name: str):
        """Get the latest post from a given Instagram profile."""
        profile = instaloader.Profile.from_username(self.loader.context, profile_name)
        posts_iterator = profile.get_posts()
        
        # Get first 10 posts and filter out pinned ones
        latest_posts = []
        for i, post in enumerate(posts_iterator):
            if i >= 10:
                break
            if not post.is_pinned:
                latest_posts.append(post)
        
        # Sort by date and return the most recent
        if latest_posts:
            return max(latest_posts, key=lambda p: p.date_utc)
        return None
    
    def get_post_by_shortcode(self, shortcode: str):
        """Get a specific post by its shortcode."""
        return instaloader.Post.from_shortcode(self.loader.context, shortcode)
    
    def get_post_by_url(self, url: str):
        """Get a specific post by its Instagram URL."""
        shortcode = self._extract_shortcode_from_url(url)
        if not shortcode:
            raise ValueError(f"Could not extract shortcode from URL: {url}")
        return self.get_post_by_shortcode(shortcode)
    
    def _extract_shortcode_from_url(self, url: str) -> Optional[str]:
        """Extract shortcode from Instagram URL."""
        # Match patterns like:
        # https://www.instagram.com/p/ABC123/
        # https://instagram.com/p/ABC123/
        # instagram.com/p/ABC123/
        # https://www.instagram.com/reel/ABC123/
        # https://instagram.com/reel/ABC123/
        # instagram.com/reel/ABC123/
        pattern = r'(?:https?://)?(?:www\.)?instagram\.com/(?:p|reel)/([A-Za-z0-9_-]+)'
        match = re.search(pattern, url)
        return match.group(1) if match else None
