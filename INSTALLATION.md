# Installing and Developing <PROJECT_NAME> (NewtCode)

This document covers installation and development setup.

---

## Project Structure

```
dev-folder/            # Root repository
│
├── folder/            # Main Python package (module source)
│   ├── __init__.py
│   ├── script.py
│   └── (other files)
│
├── tests/             # Manual and automated test scripts
│   ├── output/        # Test output logs
│   │   ├── test_*_1.txt
│   │   ├── test_*_2.txt
│   │   ├── test_*_3.txt
│   │   ├── test_*_4.txt
│   │   └── (other test logs)
│   │
│   ├── README.md      # Test documentation and instructions
│   ├── _list.sh       # (Optional) Test runner batch script
│   ├── test_*.py      # Pytest test scripts for modules
│   ├── test_*_*.py    # Pytest test scripts for functions
│   └── (other test scripts)
│
├── CHANGELOG.md       # Version history and release notes
├── CONTRIBUTING.md    # Guidelines for contributors
├── INSTALLATION.md    # Installation and development setup guide (This file)
├── LICENSE            # License file
├── pyproject.toml     # Build system configuration and project metadata
├── requirements.txt   # Project dependencies
└── README.md          # Project overview and usage instructions
```

---

## Requirements

- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13
- Python 3.14

Other dependencies are listed in `requirements.txt`.

---

## Installation Modes

### Local Installation (No PyPI)

Project <PROJECT_NAME> is a local development library and not published on PyPI.
Installation should be done directly from project folder.


### Option — Regular local installation (static copy)

Installs a copy of the package.
Recommended when only want to use project, not actively edit its source code.
Safe for non-admin users.

```bash
# Navigate to project directory
cd D:\VS_Code\dev-folder

# Install dependencies first (if requirements.txt exists)
python -m pip install --user -r requirements.txt

# Install the package for the current user
python -m pip install --user .
# OR in virtual environment (venv)
# python -m pip install .
```

- `--user` — installs into personal environment.


### Option — Editable local installation (recommended for development)

Links the library directly to working folder.
Any code changes in `dev-folder/folder/` will take effect immediately.
No reinstall needed.

```bash
# Navigate to project directory
cd D:\VS_Code\dev-folder

# Install dependencies first (if requirements.txt exists)
python -m pip install --user -r requirements.txt

# Install the package in editable mode for the current user
python -m pip install --user -e .
# OR in virtual environment (venv)
# python -m pip install -e .
```

- `--editable` or `-e` — link the project folder directly for live development


### Option — Temporary local usage (without installation)

To run or test functions directly from downloaded source.
This approach doesn't install anything globally, it only extends Python path for the current session.

```python
# Import needful modules
import sys
import os

# Adjust this path to actual project location
proj_root = os.path.join("D:", "VS_Code", "dev-folder")
# Or use one of these formats:
# proj_root = "D:/VS_Code/dev-folder"
# proj_root = r"D:\VS_Code\dev-folder"

if proj_root not in sys.path:
    sys.path.append(proj_root)

import project as Proj
```


### VS Code Settings

To make VS Code recognize local package:

1. Create or open `.vscode/settings.json`
2. Add or extend following:
    ```json
    {
      "python.analysis.extraPaths": [
        "D:/VS_Code/dev-folder"
      ]
    }
    ```
    - Adjust the paths above to match actual project location and Python interpreter path.
3. Reload VS Code (`Ctrl + Shift + P` > "Developer: Reload Window").

---

## Uninstalling

To remove the package completely:

```bash
# To check if package is installed and its location
python -m pip list | findstr project

# Uninstall the package (requires admin rights)
python -m pip uninstall project
```

---

## Usage Examples

After installation, <PROJECT_NAME> can be imported anywhere:

```python
# Import the main package (recommended - exports common functions)
import project as Proj

# Or import specific modules
import project.module as ProjMod

# Usage examples:
Proj.function("Something went wrong", arg=False)
Proj.module.function("Something went wrong", arg=False)
ProjMod.function("Something went wrong", arg=False)
```
