#!/usr/bin/env python3
"""
CLI interface for InstaDon - Instagram to Mastodon cross-posting tool.
"""

import argparse
import sys
from pathlib import Path

# Add Homebrew instaloader path to Python path
sys.path.insert(0, "/opt/homebrew/Cellar/instaloader/4.14.1/libexec/lib/python3.13/site-packages")

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
    
    args = parser.parse_args()
    
    try:
        app = InstaDon(session_file=args.session)
        result = app.post_latest_from_profile(args.profile, args.visibility)
        
        print(f"✅ Successfully created Mastodon draft!")
        print(f"Draft ID: {result.get('id')}")
        print(f"Profile: {args.profile}")
        print(f"Visibility: {args.visibility}")
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
