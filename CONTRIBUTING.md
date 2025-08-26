# Contributing to NFC Reader/Writer

Thank you for your interest in contributing to the NFC Reader/Writer project! We appreciate your time and effort in helping improve this application.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Code Style](#code-style)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)
- [Documentation](#documentation)
- [Testing](#testing)
- [License](#license)

## Code of Conduct

This project adheres to the [Contributor Covenant](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment (see below)
4. Create a new branch for your changes
5. Make your changes following the code style guide
6. Test your changes
7. Submit a pull request

## Development Environment

### Prerequisites

- Python 3.9+
- Git
- [Poetry](https://python-poetry.org/) for dependency management
- [pre-commit](https://pre-commit.com/) for git hooks

### Setup

1. Install dependencies:

   ```bash
   poetry install
   ```

2. Install pre-commit hooks:

   ```bash
   pre-commit install
   ```

3. Run the application:

   ```bash
   poetry run python main.py
   ```

## Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code
- Use [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Keep lines under 88 characters (Black formatter default)
- Use type hints for all function parameters and return values
- Write tests for new functionality

### Formatting

We use the following tools to maintain code quality:

- [Black](https://github.com/psf/black) - Code formatting
- [isort](https://pycqa.github.io/isort/) - Import sorting
- [flake8](https://flake8.pycqa.org/) - Linting
- [mypy](https://mypy.readthedocs.io/) - Static type checking

These will run automatically when you commit changes if you have pre-commit installed.

## Pull Request Process

1. Ensure your code passes all tests and linters
2. Update the documentation if needed
3. Add or update tests as needed
4. Update CHANGELOG.md with a summary of changes
5. Submit your pull request against the `main` branch
6. Request review from at least one maintainer

## Reporting Bugs

Please report bugs using the GitHub issue tracker. Include:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs. actual behavior
- Screenshots if applicable
- Your system information (OS, Python version, etc.)

## Feature Requests

We welcome feature requests! Please open an issue and:

1. Describe the feature you'd like to see
2. Explain why this would be valuable
3. Include any relevant examples or references

## Documentation

Good documentation is crucial. When adding new features or changing existing ones:

- Update relevant docstrings
- Add or update user documentation in the `docs/` directory
- Include examples where helpful
- Keep the README up to date

## Testing

We use `pytest` for testing. To run tests:

```bash
pytest
```

Please ensure:

- New code has appropriate test coverage
- All tests pass before submitting a pull request
- Tests are clear and well-documented

## License

By contributing, you agree that your contributions will be licensed under the [GPL-3.0 License](LICENSE).
