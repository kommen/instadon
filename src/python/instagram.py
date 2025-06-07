import instaloader
from typing import Optional
from datetime import datetime

class InstagramClient:
    def __init__(self, session_file: str = "kommen"):
        self.loader = instaloader.Instaloader()
        self.loader.load_session_from_file(session_file)
    
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
