#!/usr/bin/env python3
"""
CLI interface for InstaDon - Instagram to Mastodon cross-posting tool.
"""

import argparse
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from python.instadon import InstaDon


def main():
    parser = argparse.ArgumentParser(description="Cross-post from Instagram to Mastodon")
    parser.add_argument("profile", help="Instagram profile name to fetch from")
    parser.add_argument("--visibility", default="public",
                       choices=["public", "unlisted", "private", "direct"],
                       help="Mastodon post visibility (default: public)")
    parser.add_argument("--session", default="kommen",
                       help="Instagram session file name (default: kommen)")
    parser.add_argument("--tracker", default="posted_instagram_ids.txt",
                       help="File to track posted Instagram IDs (default: posted_instagram_ids.txt)")

    args = parser.parse_args()

    try:
        app = InstaDon(session_file=args.session, tracker_file=args.tracker)
        result = app.post_latest_from_profile(args.profile, args.visibility)
        
        if result["status"] == "skipped":
            print(f"⏭️  Post already processed: {result['shortcode']}")
            print(f"Instagram URL: {result['instagram_url']}")
        else:
            print(f"✅ Successfully created Mastodon draft!")
            print(f"Draft ID: {result['draft'].get('id')}")
            print(f"Instagram shortcode: {result['shortcode']}")
            print(f"Profile: {args.profile}")
            print(f"Visibility: {args.visibility}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
