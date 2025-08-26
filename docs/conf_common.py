# Common configuration for both English and Italian documentation

# Project information
project = 'NFC Reader/Writer'
copyright = '2025, Nsfr750'
author = 'Nsfr750'

# General configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    'sphinx.ext.ifconfig',
    'sphinx_copybutton',
]

# Theme options
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# HTML output
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = ['custom.css']

# Internationalization
locale_dirs = ['../locales/']
gettext_compact = False

# Copy button configuration
copybutton_prompt_text = r'\$ |>>> |\.\.\. '
copybutton_prompt_is_regexp = True
