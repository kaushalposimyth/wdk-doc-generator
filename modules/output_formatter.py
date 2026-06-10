"""
Saves generated documentation to output files and prints a summary.
"""

import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


def _slug_from_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/").replace("/", "-") or parsed.netloc.replace(".", "-")
    return re.sub(r"[^a-z0-9-]", "", path.lower())[:60]


def save_doc(markdown_content: str, url: str, output_dir: Path) -> Path:
    """Saves the generated doc as a .md file. Returns the output path."""
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
    """Prints a clean summary of what was generated."""
    print("\n" + "=" * 60)
    print("  ✅ DOCUMENTATION GENERATED")
    print("=" * 60)
    print(f"  Source URL    : {url}")
    print(f"  Doc output    : {output_path}")
    if screenshot_path:
        print(f"  Screenshot    : {screenshot_path}")
    print("=" * 60 + "\n")
