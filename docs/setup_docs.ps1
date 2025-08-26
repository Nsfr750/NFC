# Create virtual environment and install requirements
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-docs.txt

# Setup English documentation
cd ENG
sphinx-quickstart -q --sep --project="NFC Reader/Writer" --author="Nsfr750" -v "1.0.0" --language="en" --ext-autodoc --ext-viewcode --ext-todo --extensions="sphinx_rtd_theme,sphinx_copybutton" --makefile --no-batchfile .

# Setup Italian documentation
cd ..\ITA
sphinx-quickstart -q --sep --project="NFC Reade/Writer" --author="Nsfr750" -v "1.0.0" --language="it" --ext-autodoc --ext-viewcode --ext-todo --extensions="sphinx_rtd_theme,sphinx_copybutton" --makefile --no-batchfile .
