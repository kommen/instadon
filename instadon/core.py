from .instagram import InstagramClient
from .mastodon import MastodonClient
from .media import download_from_cobalt, process_cobalt_result
from .text_processor import TextProcessor
from .post_tracker import PostTracker
from typing import List
import logging

logger = logging.getLogger(__name__)

class InstaDon:
    def __init__(self, mastodon_account: str, session_file: str = "kommen", tracker_file: str = "posted_instagram_ids.txt"):
        self.instagram = InstagramClient(session_file)
        self.mastodon = MastodonClient(mastodon_account)
        self.text_processor = TextProcessor()
        self.post_tracker = PostTracker(tracker_file)
    
    def post_latest_from_profile(self, profile_name: str, visibility: str = "public"):
        """Get latest post from Instagram profile and create Mastodon draft."""
        # Get latest Instagram post
        latest_post = self.instagram.latest_post(profile_name)
        if not latest_post:
            raise ValueError(f"No posts found for profile: {profile_name}")
        
        return self._process_instagram_post(latest_post, visibility)
    
    def post_specific_post(self, instagram_url_or_shortcode: str, visibility: str = "public"):
        """Get specific Instagram post by URL or shortcode and create Mastodon post."""
        # Determine if input is URL or shortcode
        if instagram_url_or_shortcode.startswith('http') or 'instagram.com' in instagram_url_or_shortcode:
            post = self.instagram.get_post_by_url(instagram_url_or_shortcode)
        else:
            # Assume it's a shortcode
            post = self.instagram.get_post_by_shortcode(instagram_url_or_shortcode)
        
        if not post:
            raise ValueError(f"Could not find Instagram post: {instagram_url_or_shortcode}")
        
        return self._process_instagram_post(post, visibility)
    
    def _process_instagram_post(self, instagram_post, visibility: str = "public"):
        """Process an Instagram post and create Mastodon post."""
        shortcode = instagram_post.shortcode
        logger.info(f"Processing post: {shortcode}")
        
        # Check if already posted
        if self.post_tracker.is_already_posted(shortcode):
            logger.info(f"Post {shortcode} already posted to Mastodon. Skipping.")
            return {
                "status": "skipped",
                "reason": "already_posted",
                "shortcode": shortcode,
                "instagram_url": f"https://www.instagram.com/p/{shortcode}/"
            }
        
        # Build Instagram URL
        instagram_url = f"https://www.instagram.com/p/{shortcode}/"
        logger.info(f"Processing new post: {instagram_url}")
        
        try:
            # Download media using Cobalt
            cobalt_result = download_from_cobalt(instagram_url)
            media_files = process_cobalt_result(cobalt_result)
            
            if not media_files:
                raise ValueError("No media files could be downloaded")
            
            # Upload media to Mastodon
            media_ids = []
            for media_file in media_files:
                media_id = self.mastodon.upload_media(
                    str(media_file), 
                    instagram_post.caption or "Instagram post"
                )
                media_ids.append(media_id)
            
            # Process status text (summarize if needed)
            original_text = instagram_post.caption or ""
            processed_text = self.text_processor.summarize_if_needed(original_text)
            
            # Create post or thread (handles 4+ media automatically)
            posts = self.mastodon.create_post_thread(processed_text, media_ids, visibility)
            main_post = posts[0]  # First post in the thread
            
            # Mark as posted only after successful Mastodon post creation
            self.post_tracker.mark_as_posted(shortcode)
            
            # Clean up temporary files
            for media_file in media_files:
                media_file.unlink()
            
            logger.info(f"Successfully processed post {shortcode}")
            return {
                "status": "success",
                "post": main_post,
                "posts": posts,  # All posts in the thread
                "thread_length": len(posts),
                "shortcode": shortcode,
                "instagram_url": instagram_url
            }
            
        except Exception as e:
            logger.error(f"Failed to process post {shortcode}: {e}")
            # Don't mark as posted if there was an error
            raise
