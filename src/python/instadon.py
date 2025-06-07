from .instagram import InstagramClient
from .mastodon import MastodonClient
from .media import download_from_cobalt, process_cobalt_result
from .text_processor import TextProcessor
from typing import List

class InstaDon:
    def __init__(self, session_file: str = "kommen"):
        self.instagram = InstagramClient(session_file)
        self.mastodon = MastodonClient()
        self.text_processor = TextProcessor()
    
    def post_latest_from_profile(self, profile_name: str, visibility: str = "public"):
        """Get latest post from Instagram profile and create Mastodon draft."""
        # Get latest Instagram post
        latest_post = self.instagram.latest_post(profile_name)
        if not latest_post:
            raise ValueError(f"No posts found for profile: {profile_name}")
        
        # Build Instagram URL
        instagram_url = f"https://www.instagram.com/p/{latest_post.shortcode}/"
        
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
                latest_post.caption or "Instagram post"
            )
            media_ids.append(media_id)
        
        # Process status text (summarize if needed)
        original_text = latest_post.caption or ""
        processed_text = self.text_processor.summarize_if_needed(original_text)
        
        # Create draft post
        draft = self.mastodon.create_draft(processed_text, media_ids, visibility)
        
        # Clean up temporary files
        for media_file in media_files:
            media_file.unlink()
        
        return draft

# Example usage
if __name__ == "__main__":
    app = InstaDon()
    result = app.post_latest_from_profile("kulturneubau")
    print(f"Created draft: {result}")
