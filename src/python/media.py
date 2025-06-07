import requests
import tempfile
from pathlib import Path
from typing import List, Dict, Any
from .config import CONFIG

def download_from_cobalt(url: str) -> Dict[str, Any]:
    """Download media info using Cobalt API."""
    cobalt_url = CONFIG["cobalt"]["url"]
    
    response = requests.post(
        cobalt_url,
        headers={"Content-Type": "application/json"},
        json={"url": url}
    )
    response.raise_for_status()
    
    return response.json()

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
    
    if status == "picker":
        # Filter for photos and download them
        photos = [item for item in result.get("picker", []) if item.get("type") == "photo"]
        return [url_to_file(photo["url"]) for photo in photos]
    
    elif status == "tunnel":
        # Single file download
        return [url_to_file(result["url"])]
    
    else:
        return []
