# NFC Reader/Writer Documentation

This directory contains the source files for the NFC Reader/Writer documentation in both English and Italian.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Make (for building documentation)

## Setup

1. Install the required Python packages:
   ```bash
   pip install -r requirements-docs.txt
   ```

2. Set up the documentation structure:
   ```powershell
   .\setup_docs.ps1
   ```

## Building the Documentation

To build both English and Italian documentation:

```powershell
.\build_docs.ps1
```

This will generate HTML documentation in the `_build/html` directories of each language folder.

## Directory Structure

- `ENG/` - English documentation source files
- `ITA/` - Italian documentation source files
- `_templates/` - Custom Sphinx templates
- `_static/` - Static files (CSS, images, etc.)

## Adding New Content

1. Add new .rst files in the appropriate language directory
2. Update the index.rst file to include the new content
3. Rebuild the documentation

## Translation

1. Extract translatable strings:
   ```bash
   sphinx-build -b gettext -d _build/doctrees . _build/locale
   sphinx-intl update -p _build/locale -l it
   ```

2. Translate the .po files in `_build/locale/it/LC_MESSAGES/`

3. Build the translated documentation:
   ```bash
   sphinx-build -b html -D language=it . _build/html/it
   ```

## Viewing the Documentation

Open the generated HTML files in your web browser:
- English: `ENG/_build/html/index.html`
- Italian: `ITA/_build/html/index.html`

## Troubleshooting

- If you get build errors, try cleaning the build directory:
  ```bash
  make clean
  ```
  
- Ensure all dependencies are installed:
  ```bash
  pip install -r requirements-docs.txt
  ```

## License

This documentation is licensed under the same license as the main project.
