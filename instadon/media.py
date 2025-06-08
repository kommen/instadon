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

def url_to_file(url: str, suffix: str = ".jpeg") -> Path:
    """Download a file from URL to temporary file."""
    response = requests.get(url)
    response.raise_for_status()

    temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    temp_file.write(response.content)
    temp_file.close()

    return Path(temp_file.name)

def process_cobalt_result(result: Dict[str, Any]) -> List[Path]:
    """Process Cobalt download result and return list of file paths."""
    status = result.get("status")
    logger.info(f"Processing Cobalt result with status: {status}")

    if status == "picker":
        # Filter for photos and download them
        picker_items = result.get("picker", [])
        logger.info(f"Found {len(picker_items)} items in picker")

        photos = [item for item in picker_items if item.get("type") == "photo"]
        logger.info(f"Found {len(photos)} photos to download")

        for i, photo in enumerate(photos):
            logger.info(f"Photo {i+1}: {photo.get('url', 'No URL')}")

        return [url_to_file(photo["url"]) for photo in photos]

    elif status == "tunnel":
        # Single file download
        tunnel_url = result.get("url")
        logger.info(f"Single file download URL: {tunnel_url}")
        return [url_to_file(tunnel_url)]

    else:
        logger.warning(f"Unknown status '{status}' in Cobalt result")
        logger.warning(f"Full result: {result}")
        return []
