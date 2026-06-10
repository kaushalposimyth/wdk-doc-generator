"""
Saves generated documentation to output files and prints a summary.
"""

import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


def _slug_from_url(url: str) -> str:
    """Convert URL to a URL-safe slug for use in filenames.
    
    Args:
        url: The URL to convert
        
    Returns:
        URL-safe slug string (max 60 characters)
    """
    parsed = urlparse(url)
    path = parsed.path.strip("/").replace("/", "-") or parsed.netloc.replace(".", "-")
    return re.sub(r"[^a-z0-9-]", "", path.lower())[:60]


def save_doc(markdown_content: str, url: str, output_dir: Path) -> Path:
    """Save generated documentation as a timestamped markdown file.
    
    Args:
        markdown_content: The markdown content to save
        url: Source URL (used in metadata and filename)
        output_dir: Directory where the file will be saved
        
    Returns:
        Path object pointing to the saved file
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = _slug_from_url(url)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{slug}-{timestamp}.md"
    output_path = output_dir / filename

    # Add metadata header
    full_content = (
        f"---\n"
        f"source_url: {url}\n"
        f"generated_at: {datetime.now().isoformat()}\n"
        f"generator: wdk-doc-generator\n"
        f"---\n\n"
        f"{markdown_content}"
    )

    output_path.write_text(full_content, encoding="utf-8")
    return output_path


def print_summary(url: str, output_path: Path, screenshot_path: Path | None = None) -> None:
    """Print a formatted summary of generated documentation.
    
    Args:
        url: Source URL that was processed
        output_path: Path to the saved documentation file
        screenshot_path: Optional path to the saved screenshot
    """
    print("\n" + "=" * 60)
    print("  ✅ DOCUMENTATION GENERATED")
    print("=" * 60)
    print(f"  Source URL    : {url}")
    print(f"  Doc output    : {output_path}")
    if screenshot_path:
        print(f"  Screenshot    : {screenshot_path}")
    print("=" * 60 + "\n")
