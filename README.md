# 🦎 Parser MediaWiki — Configurable API crawler for multiple Wikis by `NewtCode`

Parser MediaWiki is a Python MediaWiki API crawler designed to collect content from multiple wiki installations using separate settings per wiki (endpoints, namespaces, rate limits, auth, and export rules). It retrieves pages, revisions, categories, and related metadata and normalizes the output for downstream processing. Built for repeatable runs, it helps keep large-scale wiki data collection consistent across sources.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📖 Overview

Parser MediaWiki automates the collection of wiki content through the MediaWiki API. It supports multiple wiki sources simultaneously, each with its own configuration for endpoints, namespaces, rate limiting, authentication, and export rules. The tool is designed for researchers, archivists, and developers who need to systematically collect and process large amounts of wiki data.

### Key Capabilities

- **Multi-wiki support**: Configure multiple wiki sources in separate config files
- **Namespace filtering**: Target specific content namespaces (articles, templates, categories, etc.)
- **Rate limiting**: Built-in rate limiting to respect API guidelines
- **Data normalization**: Consistent output format across different wiki sources
- **Incremental updates**: Resume interrupted collections and track changes over time
- **Content classification**: Automatic categorization of pages, redirects, and removed content

---

## 🧩 Features

### 📊 Data Collection Modes

- **All Pages**: Enumerate all pages in specified namespaces
- **Recent Changes**: Track recent edits and page modifications
- **Page Content**: Download full page content and revision history
- **Recent Page Content**: Focus on recently changed pages for incremental updates

### 🔧 Configuration Management

- **JSON-based configs**: Easy-to-edit configuration files for each wiki source
- **Namespace mapping**: Automatic namespace number-to-name conversion
- **Rate limit control**: Configurable delays between API requests
- **Output customization**: Flexible folder structures and file naming

### 📁 Output Organization

```
data/
├── raw/
│   ├── pages/          # Full page content
│   ├── redirect/       # Redirect pages
│   └── removed/        # Deleted/missing pages
├── lists/              # CSV indexes and metadata
└── logs/               # Execution logs and timestamps
```

---

## ⚙️ Requirements

- **Python 3.10+** (tested with Python 3.10, 3.11, 3.12, 3.13)
- Full type hint support with `from __future__ import annotations`

## 📦 Dependencies

All core functionality relies only on the Python Standard Library. The project uses custom utility modules (`newtutils`) for enhanced file operations, network requests, and console output.

---

## 🚀 Getting Started

See [Installation Guide](INSTALL.md) for detailed setup instructions.

---

## 📋 Usage Examples

### Running Different Collection Types

The script supports multiple collection modes:

1. **All Pages** - Complete wiki enumeration
2. **Recent Changes** - Track recent modifications
3. **Page Content** - Download full page text
4. **Recent Content** - Incremental content updates

Each mode can be selected interactively when running the script.

---

## 📋 Development Notes

- [TODO list](TODO) — Planned improvements and known issues
- [CHANGELOG](CHANGELOG.md) — Version history and release notes
- [CONTRIBUTING](CONTRIBUTING.md) — Guidelines for contributors

---

## 🪪 License & Credits

- [COPYRIGHT](COPYRIGHT) — Copyright information for original and included materials.
- [LICENSE](LICENSE) — The license governing the use of this repository (MIT).
- [AUTHORS](AUTHORS) — List of contributors and credits for external resources.
