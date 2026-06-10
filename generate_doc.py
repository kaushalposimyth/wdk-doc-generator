#!/usr/bin/env python3
"""
WDK Doc Generator
-----------------
Takes any URL → screenshots it + extracts headings/content →
writes LLM-friendly, user-friendly documentation using Claude.

Usage:
    python generate_doc.py <URL> [options]

Examples:
    python generate_doc.py https://learn.wdesignkit.com/docs/wdesignkit-mcp-abilities/
    python generate_doc.py https://learn.wdesignkit.com/docs/getting-started/ --no-screenshot
    python generate_doc.py https://learn.wdesignkit.com/docs/widget-builder/ --context "WDesignKit widget builder for Elementor"

NOTE: This tool ONLY reads from URLs. It never modifies any live site.
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env from config/ or project root
load_dotenv(Path(__file__).parent / "config" / ".env")
load_dotenv(Path(__file__).parent / ".env")

from modules.page_scraper import (
    extract_page_structure,
    format_structure_for_prompt,
    screenshot_page,
    image_to_base64,
)
from modules.doc_writer import write_doc
from modules.output_formatter import save_doc, print_summary


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate LLM-friendly documentation from any URL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("url", help="URL of the page to document")
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory to save generated docs (default: output/)",
    )
    parser.add_argument(
        "--no-screenshot",
        action="store_true",
        help="Skip taking a screenshot (faster, text-only mode)",
    )
    parser.add_argument(
        "--context",
        default="",
        help="Optional product context to help Claude write better docs",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
        help="Claude model ID (default: claude-sonnet-4-6)",
    )
    parser.add_argument(
        "--viewport-width",
        type=int,
        default=int(os.getenv("VIEWPORT_WIDTH", "1440")),
        help="Screenshot viewport width (default: 1440)",
    )
    parser.add_argument(
        "--viewport-height",
        type=int,
        default=int(os.getenv("VIEWPORT_HEIGHT", "900")),
        help="Screenshot viewport height (default: 900)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY not set.")
        print("   Copy config/.env.example to config/.env and add your API key.")
        sys.exit(1)

    url = args.url
    output_dir = Path(args.output_dir)
    screenshots_dir = output_dir / "screenshots"

    print(f"\n🔍 Processing: {url}")
    print("   (Read-only — your live site will NOT be modified)\n")

    # Step 1: Extract page structure
    print("📄 Step 1/3 — Extracting page structure...")
    try:
        structure = extract_page_structure(url)
        structure_text = format_structure_for_prompt(structure)
        headings_count = len(structure["headings"])
        blocks_count = len(structure["content_blocks"])
        print(f"   ✓ Found {headings_count} headings, {blocks_count} content blocks")
    except Exception as e:
        print(f"   ❌ Failed to extract page structure: {e}")
        sys.exit(1)

    # Step 2: Screenshot
    screenshot_b64 = None
    screenshot_path = None

    if not args.no_screenshot:
        print("📸 Step 2/3 — Taking screenshot...")
        try:
            screenshot_path = screenshot_page(
                url,
                screenshots_dir,
                viewport_width=args.viewport_width,
                viewport_height=args.viewport_height,
            )
            screenshot_b64 = image_to_base64(screenshot_path)
            size_kb = screenshot_path.stat().st_size // 1024
            print(f"   ✓ Screenshot saved ({size_kb}KB): {screenshot_path.name}")
        except Exception as e:
            print(f"   ⚠ Screenshot failed (continuing without it): {e}")
    else:
        print("📸 Step 2/3 — Screenshot skipped (--no-screenshot)")

    # Step 3: Generate documentation
    print(f"✍️  Step 3/3 — Writing documentation with Claude ({args.model})...")
    try:
        doc_markdown = write_doc(
            page_structure_text=structure_text,
            screenshot_base64=screenshot_b64,
            product_context=args.context,
            model=args.model,
        )
        print(f"   ✓ Documentation generated ({len(doc_markdown)} chars)")
    except Exception as e:
        print(f"   ❌ Failed to generate documentation: {e}")
        sys.exit(1)

    # Save output
    output_path = save_doc(doc_markdown, url, output_dir)
    print_summary(url, output_path, screenshot_path)

    # Print preview of first 500 chars
    preview = doc_markdown[:500].strip()
    print("--- PREVIEW ---")
    print(preview)
    if len(doc_markdown) > 500:
        print("...\n[truncated — see full file]")
    print()


if __name__ == "__main__":
    main()
