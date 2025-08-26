# Activate virtual environment
.venv\Scripts\activate

# Build English documentation
Write-Host "Building English documentation..." -ForegroundColor Green
cd ENG
make clean
make html
cd ..

# Build Italian documentation
Write-Host "`nBuilding Italian documentation..." -ForegroundColor Green
cd ITA
make clean
make html
cd ..

Write-Host "`nDocumentation build complete!" -ForegroundColor Green
Write-Host "English docs: file://$PWD/ENG/_build/html/index.html"
Write-Host "Italian docs: file://$PWD/ITA/_build/html/index.html"
