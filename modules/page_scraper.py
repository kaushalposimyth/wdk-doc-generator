"""
Scrapes a URL: takes a full-page screenshot and extracts structured content
(headings, paragraphs, code blocks, lists, notes) using Playwright + BeautifulSoup.
"""

import base64
import re
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def _slug_from_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/").replace("/", "-") or parsed.netloc.replace(".", "-")
    return re.sub(r"[^a-z0-9-]", "", path.lower())[:60]


def screenshot_page(url: str, output_dir: Path, viewport_width: int = 1440, viewport_height: int = 900) -> Path:
    """Takes a full-page screenshot and saves it. Returns the image path."""
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = _slug_from_url(url)
    img_path = output_dir / f"{slug}-screenshot.png"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": viewport_width, "height": viewport_height})
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)
        page.screenshot(path=str(img_path), full_page=True)
        browser.close()

    return img_path


def image_to_base64(img_path: Path) -> str:
    with open(img_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def extract_page_structure(url: str) -> dict:
    """
    Fetches the URL and extracts structured content:
    - title, meta description
    - headings hierarchy (H1-H6)
    - paragraphs, lists, code blocks, tables
    - returns a clean dict ready for the doc writer
    """
    import requests

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    # Remove clutter
    for tag in soup.select("script, style, nav, footer, header, .sidebar, .advertisement, [class*='cookie'], [class*='popup'], [class*='banner']"):
        tag.decompose()

    # Meta
    title = soup.find("title")
    title_text = title.get_text(strip=True) if title else ""

    meta_desc = soup.find("meta", attrs={"name": "description"})
    description = meta_desc.get("content", "") if meta_desc else ""

    # Heading hierarchy
    headings = []
    for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        text = tag.get_text(strip=True)
        if text:
            headings.append({"level": int(tag.name[1]), "text": text})

    # Main content blocks
    main = soup.find("main") or soup.find("article") or soup.find("body")
    content_blocks = []

    for element in main.descendants:
        if not hasattr(element, "name") or not element.name:
            continue

        tag_name = element.name.lower()

        if tag_name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            text = element.get_text(strip=True)
            if text:
                content_blocks.append({"type": "heading", "level": int(tag_name[1]), "text": text})

        elif tag_name == "p":
            text = element.get_text(strip=True)
            if text and len(text) > 20:
                content_blocks.append({"type": "paragraph", "text": text})

        elif tag_name in ("ul", "ol"):
            items = [li.get_text(strip=True) for li in element.find_all("li", recursive=False) if li.get_text(strip=True)]
            if items:
                content_blocks.append({"type": "list", "ordered": tag_name == "ol", "items": items})

        elif tag_name in ("pre", "code"):
            code_text = element.get_text()
            if code_text.strip() and len(code_text.strip()) > 10:
                lang = element.get("class", [""])[0].replace("language-", "") if element.get("class") else ""
                content_blocks.append({"type": "code", "language": lang, "text": code_text.strip()})

        elif tag_name == "table":
            rows = []
            for tr in element.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                if cells:
                    rows.append(cells)
            if rows:
                content_blocks.append({"type": "table", "rows": rows})

        elif tag_name in ("blockquote", "aside"):
            text = element.get_text(strip=True)
            if text:
                content_blocks.append({"type": "note", "text": text})

    # Deduplicate adjacent identical blocks
    deduped = []
    for block in content_blocks:
        if not deduped or deduped[-1] != block:
            deduped.append(block)

    return {
        "url": url,
        "title": title_text,
        "description": description,
        "headings": headings,
        "content_blocks": deduped,
    }


def format_structure_for_prompt(structure: dict) -> str:
    """Converts extracted structure into a clean text prompt-friendly format."""
    lines = []
    lines.append(f"PAGE URL: {structure['url']}")
    lines.append(f"PAGE TITLE: {structure['title']}")
    if structure["description"]:
        lines.append(f"META DESCRIPTION: {structure['description']}")

    lines.append("\n--- HEADING HIERARCHY ---")
    for h in structure["headings"]:
        indent = "  " * (h["level"] - 1)
        lines.append(f"{indent}H{h['level']}: {h['text']}")

    lines.append("\n--- CONTENT STRUCTURE ---")
    for block in structure["content_blocks"]:
        btype = block["type"]
        if btype == "heading":
            lines.append(f"\n{'#' * block['level']} {block['text']}")
        elif btype == "paragraph":
            lines.append(f"\n{block['text']}")
        elif btype == "list":
            prefix = "1." if block["ordered"] else "-"
            for i, item in enumerate(block["items"], 1):
                p = f"{i}." if block["ordered"] else "-"
                lines.append(f"  {p} {item}")
        elif btype == "code":
            lang = block.get("language", "")
            lines.append(f"\n```{lang}\n{block['text']}\n```")
        elif btype == "table":
            for row in block["rows"]:
                lines.append("| " + " | ".join(row) + " |")
        elif btype == "note":
            lines.append(f"\n> {block['text']}")

    return "\n".join(lines)
