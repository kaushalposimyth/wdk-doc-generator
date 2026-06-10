#!/usr/bin/env python3
"""
Batch Doc Generator
-------------------
Process multiple URLs from a text file or inline list.

Usage:
    python batch_generate.py urls.txt
    python batch_generate.py urls.txt --no-screenshot --context "WDesignKit docs"

urls.txt format (one URL per line, # for comments):
    # Getting Started docs
    https://learn.wdesignkit.com/docs/getting-started/
    https://learn.wdesignkit.com/docs/widget-builder/
    https://learn.wdesignkit.com/docs/wdesignkit-mcp-abilities/
"""

import argparse
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / "config" / ".env")
load_dotenv(Path(__file__).parent / ".env")

from modules.page_scraper import extract_page_structure, format_structure_for_prompt, screenshot_page, image_to_base64
from modules.doc_writer import write_doc
from modules.output_formatter import save_doc


def parse_args():
    parser = argparse.ArgumentParser(description="Batch generate docs from a list of URLs")
    parser.add_argument("urls_file", help="Text file with one URL per line")
    parser.add_argument("--output-dir", default="output", help="Output directory (default: output/)")
    parser.add_argument("--no-screenshot", action="store_true", help="Skip screenshots")
    parser.add_argument("--context", default="", help="Product context for the AI")
    parser.add_argument("--model", default=os.getenv("AI_MODEL", "gpt-4o-mini"))
    parser.add_argument("--delay", type=float, default=2.0, help="Seconds between requests (default: 2)")
    return parser.parse_args()


def load_urls(filepath: str) -> list[str]:
    """Load URLs from a text file, skipping comments and empty lines.
    
    Args:
        filepath: Path to text file with one URL per line
        
    Returns:
        List of valid URLs
    """
    urls = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    return urls


def main():
    args = parse_args()

    if not os.getenv("AI_API_KEY"):
        print("❌ AI_API_KEY not set. Copy config/.env.example to config/.env")
        sys.exit(1)

    urls = load_urls(args.urls_file)
    if not urls:
        print("❌ No URLs found in file.")
        sys.exit(1)

    output_dir = Path(args.output_dir)
    screenshots_dir = output_dir / "screenshots"
    total = len(urls)

    print(f"\n🚀 Batch generating docs for {total} URLs")
    print(f"   Output: {output_dir}/\n")

    results = {"success": [], "failed": []}

    for i, url in enumerate(urls, 1):
        print(f"[{i}/{total}] {url}")

        try:
            structure = extract_page_structure(url)
            structure_text = format_structure_for_prompt(structure)

            screenshot_b64 = None
            if not args.no_screenshot:
                try:
                    img_path = screenshot_page(url, screenshots_dir)
                    screenshot_b64 = image_to_base64(img_path)
                except Exception as e:
                    print(f"  ⚠ Screenshot failed: {e}")

            doc_markdown = write_doc(
                page_structure_text=structure_text,
                screenshot_base64=screenshot_b64,
                product_context=args.context,
                model=args.model,
            )

            output_path = save_doc(doc_markdown, url, output_dir)
            print(f"  ✅ Saved: {output_path.name}")
            results["success"].append(url)

        except Exception as e:
            print(f"  ❌ Failed: {e}")
            results["failed"].append((url, str(e)))

        if i < total:
            time.sleep(args.delay)

    print(f"\n{'='*50}")
    print(f"  Done: {len(results['success'])}/{total} succeeded")
    if results["failed"]:
        print(f"  Failed ({len(results['failed'])}):")
        for url, err in results["failed"]:
            print(f"    - {url}: {err}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
