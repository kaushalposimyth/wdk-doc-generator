# WDK Doc Generator

Automatically generate LLM-friendly, user-friendly documentation from any URL.

**How it works:**
1. Takes a full-page screenshot (1440px wide)
2. Extracts all headings, paragraphs, lists, code blocks, and tables
3. Uses AI to write clean, structured Markdown documentation
4. Saves the output to the `output/` folder

> **Read-only tool** — it never modifies your live site. It only reads from URLs.

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure API key

```bash
cp config/.env.example config/.env
```

Edit `config/.env` and add your AI API key:
```
AI_API_KEY=your-key-here
```

Get your key at: https://console.anthropic.com

---

## Usage

### Single URL

```bash
python generate_doc.py https://learn.wdesignkit.com/docs/wdesignkit-mcp-abilities/
```

With product context (improves output quality):
```bash
python generate_doc.py https://learn.wdesignkit.com/docs/widget-builder/ \
  --context "WDesignKit is a Figma-to-Elementor design tool for WordPress"
```

Without screenshot (faster, text-only):
```bash
python generate_doc.py https://learn.wdesignkit.com/docs/getting-started/ --no-screenshot
```

### Batch Mode (multiple URLs)

Edit `example-urls.txt` with your URLs, then:
```bash
python batch_generate.py example-urls.txt --context "WDesignKit docs"
```

---

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--output-dir` | `output/` | Where to save generated docs |
| `--no-screenshot` | off | Skip screenshot, text-only mode |
| `--context` | _(empty)_ | Extra product context for better output |
| `--model` | `default` | AI model to use |
| `--viewport-width` | `1440` | Screenshot width in pixels |
| `--viewport-height` | `900` | Screenshot height in pixels |

---

## Output

Generated docs are saved to `output/` as Markdown files:
```
output/
├── docs-wdesignkit-mcp-abilities-20260610-143000.md
└── screenshots/
    └── docs-wdesignkit-mcp-abilities-screenshot.png
```

Each doc includes a YAML frontmatter header with `source_url` and `generated_at`.

---

## Doc Structure (auto-generated)

Every generated doc follows this structure:

1. **H1 Title** — clear, descriptive name
2. **Intro paragraph** — what this is and why it matters
3. **Prerequisites** (if applicable)
4. **Main sections** — based on page headings
5. **Step-by-step instructions** — numbered where relevant
6. **Feature lists** — bullet points with short descriptions
7. **Code examples** — fenced blocks with language labels
8. **Notes/Tips** — in blockquotes
9. **Key Takeaways** — 3-5 bullet points at the end

---

## Requirements

- Python 3.10+
- `AI_API_KEY` environment variable
- Chromium (installed via `playwright install chromium`)

---

## Built by

**POSIMYTH Innovations** — [wdesignkit.com](https://wdesignkit.com)
