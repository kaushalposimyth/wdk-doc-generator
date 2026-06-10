"""
Sends page structure + screenshot to the AI model and generates
LLM-friendly, user-friendly documentation in WDesignKit style.
"""

import os
import anthropic


SYSTEM_PROMPT = """You are a professional technical documentation writer specializing in LLM-friendly, user-friendly documentation.

Your job: Given a page screenshot and its extracted content structure, write comprehensive, well-organized documentation for that page/feature.

DOCUMENTATION STYLE RULES:
1. **LLM-Friendly**: Use clear, direct language. Structure with proper headings. Avoid fluff. Every sentence should convey information.
2. **User-Friendly**: Write for beginners. Use simple words. Explain WHY not just WHAT.
3. **Format**: Write in clean Markdown with proper heading hierarchy (H1 → H2 → H3).
4. **Structure every doc with**:
   - Brief intro paragraph (what this is, why it matters)
   - Prerequisites (if any)
   - Main content sections (based on the page headings)
   - Step-by-step instructions where applicable (numbered lists)
   - Feature/ability lists as clean bullet points with short descriptions
   - Code examples in fenced code blocks with language labels
   - Notes/tips in blockquotes (> **Note:** ...)
   - A "Key Takeaways" section at the end (3-5 bullet points)
5. **DO NOT**: Copy content verbatim. Rewrite clearly. Don't invent features not present in the source. Don't add marketing fluff.
6. **Tone**: Helpful, clear, professional but approachable. Like explaining to a smart colleague.

OUTPUT: Pure markdown. No preamble. Start directly with the H1 heading."""


def write_doc(
    page_structure_text: str,
    screenshot_base64: str | None = None,
    product_context: str = "",
    model: str = "claude-sonnet-4-6",
) -> str:
    """Generate professional documentation from page structure.

    Args:
        page_structure_text: Formatted structure from page_scraper.format_structure_for_prompt()
        screenshot_base64: Optional base64-encoded PNG screenshot for visual context
        product_context: Optional product context to help write relevant docs
        model: AI model ID

    Returns:
        Generated documentation as a markdown string

    Raises:
        Exception: If the API call fails
    """
    api_key = os.environ.get("AI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("AI_API_KEY not set. Add it to config/.env")

    client = anthropic.Anthropic(api_key=api_key)

    user_content = []

    if screenshot_base64:
        user_content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": screenshot_base64,
            },
        })

    context_note = f"\n\nPRODUCT CONTEXT: {product_context}" if product_context else ""

    user_content.append({
        "type": "text",
        "text": (
            f"Write comprehensive documentation for this page.{context_note}\n\n"
            f"Here is the extracted page structure:\n\n{page_structure_text}\n\n"
            "Generate LLM-friendly, user-friendly documentation in clean Markdown. "
            "Use the screenshot for visual context to understand the UI and layout. "
            "Write clear, structured docs that both humans and AI tools can easily understand."
        ),
    })

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )

    return response.content[0].text
