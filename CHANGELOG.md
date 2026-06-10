# Changelog

All notable changes to the WDK Doc Generator project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.1] - 2026-06-10 (Today)

### Added
- **Module Documentation**: Added comprehensive module-level docstring to `modules/__init__.py` with version and author metadata
- **Function Docstrings**: Enhanced all function docstrings across modules with detailed parameter and return descriptions:
  - `page_scraper.py`: `_slug_from_url()`, `extract_page_structure()`, `format_structure_for_prompt()`, `image_to_base64()`
  - `output_formatter.py`: `save_doc()`, `print_summary()`, `_slug_from_url()`
  - `doc_writer.py`: `write_doc()` with added Raises section
  - `batch_generate.py`: `load_urls()` with improved documentation

### Improved
- Better code documentation for developer clarity
- Enhanced IDE autocomplete support through improved docstrings
- Standardized docstring format across all modules (Args, Returns, Raises sections)
- Better error documentation with exception types

### Fixed
- Added missing docstring sections to support better code introspection

---

## [1.0.0] - 2026-06-09 (1 day ago)

### Added
- **Initial Project Release**: WDK Doc Generator - Automated LLM-friendly documentation generator from URLs
- **Core Features**:
  - Full-page screenshot capture (1440px wide using Playwright)
  - Structured content extraction (headings, paragraphs, lists, code blocks, tables)
  - AI integration for intelligent documentation writing
  - Batch processing support for multiple URLs
  - Markdown output with metadata headers

- **Main Scripts**:
  - `generate_doc.py`: Single URL documentation generator with CLI options
  - `batch_generate.py`: Process multiple URLs from text files

- **Core Modules**:
  - `modules/page_scraper.py`: URL scraping, screenshot, and content extraction
  - `modules/doc_writer.py`: AI API integration for doc generation
  - `modules/output_formatter.py`: File saving and summary printing

- **Configuration**:
  - Environment variable support via `.env` files
  - Configurable viewport sizes, models, and output directories
  - Support for product context in documentation generation

- **Documentation**:
  - Comprehensive README with setup instructions
  - Example URLs file for batch processing
  - Environment configuration template

### Configuration Options
- `AI_API_KEY`: AI API authentication
- `AI_MODEL`: Model selection
- `VIEWPORT_WIDTH`: Screenshot width (default: 1440px)
- `VIEWPORT_HEIGHT`: Screenshot height (default: 900px)
- `OUTPUT_DIR`: Documentation output directory (default: output/)

### Dependencies
- `requests`: AI API requests
- `playwright`: Browser automation for screenshots
- `beautifulsoup4`: HTML parsing
- `python-dotenv`: Environment configuration

---

## Release Notes

### v1.0.1 Release Highlights
✅ **Documentation Quality**: Significantly improved code documentation with standardized docstrings across all modules  
✅ **Developer Experience**: Better IDE support and code clarity for future maintainers  
✅ **Best Practices**: Implemented Python package standards with module metadata  

### v1.0.0 Release Highlights
✅ **Full Feature Set**: Complete solution for generating documentation from any URL  
✅ **AI-Powered**: Uses AI for intelligent, LLM-friendly documentation  
✅ **Production Ready**: Batch processing and extensive configuration options  
✅ **Read-Only Safe**: Tool never modifies live sites, only reads and generates docs  

---

## Planned Features (Roadmap)

- [ ] Support for different documentation styles (technical, tutorial, API reference)
- [ ] Custom output format templates
- [ ] Multi-language documentation support
- [ ] Integration with documentation platforms (GitBook, Confluence, etc.)
- [ ] Performance optimization for large-scale batch processing
- [ ] Cache system for repeated URLs
- [ ] Custom CSS handling for better content extraction

---

## How to Contribute

See README.md for setup instructions and contribution guidelines.

---

## Version History
| Version | Date | Type | Changes |
|---------|------|------|---------|
| 1.0.1 | 2026-06-10 | Docs | Documentation improvements & code quality enhancements |
| 1.0.0 | 2026-06-09 | Release | Initial project release with core features |
