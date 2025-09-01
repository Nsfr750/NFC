# Contributing to NFC Tool

Thank you for your interest in contributing to the NFC Tool! We appreciate your time and effort in making this project better.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Reporting Issues](#reporting-issues)
- [Feature Requests](#feature-requests)
- [Donations and Sponsorships](#donations-and-sponsorships)

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment (see below)
4. Create a feature branch for your changes
5. Make your changes
6. Test your changes
7. Submit a pull request

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/NFC.git
   cd NFC
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Unix or MacOS:
   source venv/bin/activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   pre-commit install
   ```

4. **Run the application in development mode**
   ```bash
   python -m nfctool --dev
   ```

## Making Changes

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/issue-number-description
   ```

2. Make your changes following the coding standards
3. Write or update tests as needed
4. Update documentation
5. Run tests and verify everything passes

## Pull Request Process

1. Ensure all tests pass
2. Update the CHANGELOG.md with your changes
3. Update the documentation if needed
4. Submit a pull request to the `main` branch
5. Address any code review feedback
6. Once approved, a maintainer will merge your PR

## Coding Standards

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code
- Use type hints for all new code
- Keep functions small and focused
- Write meaningful commit messages
- Use descriptive variable and function names
- Add docstrings to all public functions and classes

## Testing

Run the test suite:

```bash
pytest
```

We aim for 80%+ test coverage. You can check the coverage with:

```bash
pytest --cov=nfctool tests/
```

## Documentation

- Update documentation when adding new features or changing behavior
- Follow the existing documentation style
- Add docstrings to all public functions and classes
- Update README.md if needed

## Reporting Issues

When reporting issues, please include:

1. A clear title and description
2. Steps to reproduce the issue
3. Expected and actual behavior
4. Environment details (OS, Python version, etc.)
5. Any relevant error messages or logs

## Feature Requests

We welcome feature requests! Please:

1. Search existing issues to avoid duplicates
2. Describe the feature and why it would be useful
3. Include any relevant use cases or examples

## Donations and Sponsorships

If you find this project useful, consider supporting its development:

- [Donate via PayPal](https://paypal.me/3dmega)
- [Become a Patron](https://www.patreon.com/Nsfr750)
- Donate Monero: `47Jc6MC47WJVFhiQFYwHyBNQP5BEsjUPG6tc8R37FwcTY8K5Y3LvFzveSXoGiaDQSxDrnCUBJ5WBj6Fgmsfix8VPD4w3gXF`

## License

By contributing, you agree that your contributions will be licensed under the GPLv3 License.
