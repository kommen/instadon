#!/usr/bin/env python3
"""
CLI interface for InstaDon - Instagram to Mastodon cross-posting tool.
"""

import argparse
import sys
from pathlib import Path

from .core import InstaDon


def main():
    parser = argparse.ArgumentParser(description="Cross-post from Instagram to Mastodon")

    # Create mutually exclusive group for profile vs URL
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("profile", nargs="?", help="Instagram profile name to fetch latest post from")
    source_group.add_argument("--url", help="Specific Instagram post URL to cross-post")

    parser.add_argument("--visibility", default="public",
                       choices=["public", "unlisted", "private", "direct"],
                       help="Mastodon post visibility (default: public)")
    parser.add_argument("--session", default="kommen",
                       help="Instagram session file name (default: kommen)")
    parser.add_argument("--tracker", default="posted_instagram_ids.txt",
                       help="File to track posted Instagram IDs")
    parser.add_argument("--account", required=True,
                       help="Mastodon account to post to (required)")

    args = parser.parse_args()

    try:
        app = InstaDon(mastodon_account=args.account, session_file=args.session, tracker_file=args.tracker)

        # Choose between profile latest post or specific URL
        if args.url:
            result = app.post_specific_post(args.url, args.visibility)
            source_info = f"URL: {args.url}"
        else:
            result = app.post_latest_from_profile(args.profile, args.visibility)
            source_info = f"Profile: {args.profile}"

        if result["status"] == "skipped":
            print(f"⏭️  Post already processed: {result['shortcode']}")
            print(f"Instagram URL: {result['instagram_url']}")
        else:
            print(f"✅ Successfully created Mastodon post!")
            print(f"Post ID: {result['post'].get('id')}")
            print(f"Instagram shortcode: {result['shortcode']}")
            print(f"Source: {source_info}")
            print(f"Mastodon account: {args.account}")
            print(f"Visibility: {args.visibility}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
