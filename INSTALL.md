# ⚙️ Installing and Developing Parser MediaWiki

This guide covers installation, configuration, and development setup for Parser MediaWiki.

---

## 🧱 Project Structure

```
dev-parser-mediawiki/  # Root repository
│
├── mwparser/          # Main Python package
│   ├── configs/       # Configuration files for different wikis
│   │   └── xxx.json   # Template config file
│   │
│   └── script.py      # Main parser script
│
├── AUTHORS            # Project contributors
├── CHANGELOG.md       # Version history and release notes
├── CONTRIBUTING.md    # Guidelines for contributors
├── COPYRIGHT          # Copyright information
├── INSTALL.md         # This installation guide
├── LICENSE            # MIT License
├── TODO               # Development task list
└── README.md          # Project overview and usage instructions

result-wiki-name/
├── data/              # Generated data directory (created automatically)
│   ├── raw/           # Raw wiki content
│   │   ├── pages/     # Full page content files
│   │   ├── redirect/  # Redirect page content
│   │   └── removed/   # Missing/deleted pages
│   ├── lists/         # CSV index files and metadata
│   └── logs/          # Execution logs and timestamps
```

---

## 📦 Requirements

### System Requirements

- **Python 3.10 - 3.13**
- **pip** or **conda** for package management
- **4GB+ RAM** recommended for large wiki processing
- **Stable internet connection** for API access

### Python Dependencies

Parser MediaWiki uses only the Python Standard Library plus custom utility modules:

- `sys`, `os`, `datetime` - Core system operations
- `shutil`, `re` - File operations and regular expressions
- `newtutils` - My Custom utilities for file/network/console operations

---

## 🚀 Installation and Configuration

### Clone the Repository

```bash
# Clone the repository
git clone https://github.com/AnnaBurova/dev-parser-mediawiki.git
cd dev-parser-mediawiki
```

### Verify Python Version

```bash
# Check Python version
python --version
# Should show Python 3.10.x, 3.11.x, 3.12.x, or 3.13.x
```

### Setting up Wiki Configurations

**Copy the template config**:

```bash
cp  mwparser/configs/xxx.json  mwparser/configs/wiki.json
```

**Adjust your configuration file**:

```json
{
  "FOLDER_LINK": "result-wiki-name",
  "BASE_URL": "https://wiki.example.com/api.php"
}
```

**Configuration Parameters**:

- `FOLDER_LINK`: Output directory name for this wiki's data
- `BASE_URL`: Full URL to the wiki's MediaWiki API endpoint

### Advanced Configuration

For more complex setups, you may need to:

1. **Set up namespace mappings** in `result-wiki-name/data/schemas/namespace_types.json`
2. **Configure rate limiting** in the script parameters
3. **Set up authentication** for private wikis
4. **Configure blocked pages list** in `result-wiki-name/data/lists/blocked.txt`

---

## 🏃‍♂️ Running the Parser

### Basic Usage

```bash
# Navigate to project directory
cd /path/to/dev-parser-mediawiki

# Run the parser
python mwparser/script.py
```

### Interactive Mode

The script will prompt you to:

1. **Select a configuration** from available config files
2. **Choose collection type**:
  - All Pages: Complete wiki enumeration
  - Recent Changes: Track recent modifications
  - Page Content: Download full page content
  - Recent Content: Incremental updates

### Command Line Options

The script supports several configuration variables that can be modified at the top of `script.py`:

```python
# Configuration variables
choose_config = "wiki.json"          # Specific config file
check_config_folder = True           # Interactive config selection
save_log = True                      # Enable logging to file
```

### Running Specific Operations

```python
# Pre-configure for specific operations
choose_config = "wiki.json"
config_type_list = {
  "1": "allpages",      # Enumerate all pages
  "2": "pageids",       # Download page content
  "3": "recentchanges", # Get recent changes
  "4": "pagesrecent",   # Recent page content
}
```

---

## 🔧 Development Setup

### For Contributors

1. **Fork and clone** the repository
2. **Set up development environment** as described above
3. **Install development dependencies** (if any are added)
4. **Run tests** (when test suite is implemented)
- **Follow contribution guidelines** in [CONTRIBUTING.md](CONTRIBUTING.md)
- Use `from __future__ import annotations` in all Python files
- Follow Google-style docstrings
- Use explicit type hints
- Respect `.gitattributes` for line endings

### Testing

Currently, the project does not have automated tests. When contributing:

- Test your changes manually with different wiki sources
- Verify output format consistency
- Check error handling for network issues
- Validate configuration file parsing

---

## 🐛 Troubleshooting

### Common Issues

**"No config selected" error:**

- Ensure config files exist in `mwparser/configs/`
- Check file permissions and JSON syntax

**API rate limiting:**

- The script includes built-in rate limiting
- Adjust `maxlag` parameter in the code if needed

**Memory issues with large wikis:**

- Process namespace-by-namespace instead of all at once
- Use the pageids mode for incremental processing

**Permission errors:**

- Ensure write access to the data directory
- Check antivirus software isn't blocking file operations

### Getting Help

- Check the [TODO](TODO) file for known issues
- Review [CHANGELOG](CHANGELOG.md) for recent changes
- Open an issue on GitHub for bugs or feature requests

---

## 📋 Next Steps

After installation:

1. **Try the example configs** with Guild Wars wikis
2. **Create your own config** for a wiki you want to parse
3. **Review the output structure** and customize as needed
4. **Set up automated runs** using cron or task scheduler
5. **Contribute improvements** back to the project

For detailed API documentation and advanced usage, see the code comments in `mwparser/script.py`.
