import requests
import tempfile
import logging
from pathlib import Path
from typing import List, Dict, Any
from .config import CONFIG

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_from_cobalt(url: str) -> Dict[str, Any]:
    """Download media info using Cobalt API."""
    cobalt_url = CONFIG["cobalt"]["url"]

    logger.info(f"Requesting media from Cobalt API: {cobalt_url}")
    logger.info(f"Instagram URL: {url}")

    payload = {"url": url}
    headers = {"Content-Type": "application/json",
               "Accept": "application/json"}

    logger.info(f"Request payload: {payload}")
    logger.info(f"Request headers: {headers}")

    try:
        response = requests.post(
            cobalt_url,
            headers=headers,
            json=payload
        )

        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response headers: {dict(response.headers)}")

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code} error from Cobalt API")
            logger.error(f"Response text: {response.text}")

        response.raise_for_status()

        result = response.json()
        logger.info(f"Cobalt API response: {result}")

        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Error response text: {e.response.text}")
        raise

def url_to_file(url: str, suffix: str = None) -> Path:
    """Download a file from URL to temporary file."""
    response = requests.get(url)
    response.raise_for_status()

    # Auto-detect file extension if not provided
    if suffix is None:
        content_type = response.headers.get('content-type', '')
        if 'video' in content_type:
            suffix = ".mp4"
        elif 'image' in content_type:
            suffix = ".jpeg"
        else:
            # Default based on URL extension or fallback to .jpeg
            if any(ext in url.lower() for ext in ['.mp4', '.mov', '.avi']):
                suffix = ".mp4"
            else:
                suffix = ".jpeg"

    temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    temp_file.write(response.content)
    temp_file.close()

    return Path(temp_file.name)

def process_cobalt_result(result: Dict[str, Any]) -> List[Path]:
    """Process Cobalt download result and return list of file paths."""
    status = result.get("status")
    logger.info(f"Processing Cobalt result with status: {status}")

    if status == "picker":
        # Filter for photos and videos and download them
        picker_items = result.get("picker", [])
        logger.info(f"Found {len(picker_items)} items in picker")

        media_items = [item for item in picker_items if item.get("type") in ["photo", "video"]]
        logger.info(f"Found {len(media_items)} media items to download")

        for i, media_item in enumerate(media_items):
            item_type = media_item.get("type", "unknown")
            logger.info(f"Media {i+1} ({item_type}): {media_item.get('url', 'No URL')}")

        return [url_to_file(media_item["url"]) for media_item in media_items]

    elif status == "tunnel":
        # Single file download
        tunnel_url = result.get("url")
        logger.info(f"Single file download URL: {tunnel_url}")
        return [url_to_file(tunnel_url)]

    elif status == "redirect":
        # Direct file download with redirect URL
        redirect_url = result.get("url")
        filename = result.get("filename", "")
        logger.info(f"Redirect download URL: {redirect_url}")
        logger.info(f"Suggested filename: {filename}")
        
        # Extract file extension from filename if available
        suffix = None
        if filename:
            if filename.lower().endswith('.mp4'):
                suffix = ".mp4"
            elif filename.lower().endswith(('.jpg', '.jpeg')):
                suffix = ".jpeg"
        
        return [url_to_file(redirect_url, suffix)]

    else:
        logger.warning(f"Unknown status '{status}' in Cobalt result")
        logger.warning(f"Full result: {result}")
        return []
