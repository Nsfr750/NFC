.. _contributing:

Contributing to NFC Reader/Writer
================================

Thank you for your interest in contributing to the NFC Reader/Writer project! We welcome all types of contributions, including bug reports, feature requests, documentation improvements, and code contributions.

How to Contribute
----------------

1. **Fork the Repository**
   - Click the "Fork" button on the `GitHub repository page <https://github.com/Nsfr750/NFC>`_
   - Clone your forked repository to your local machine

2. **Set Up Development Environment**
   - Create a virtual environment:
     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows: venv\Scripts\activate
     ```
   - Install development dependencies:
     ```bash
     pip install -r requirements-dev.txt
     ```

3. **Create a Branch**
   - Create a new branch for your changes:
     ```bash
     git checkout -b feature/your-feature-name
     ```

4. **Make Your Changes**
   - Follow the coding style guidelines (PEP 8)
   - Write tests for new features
   - Update documentation as needed

5. **Test Your Changes**
   - Run the test suite:
     ```bash
     pytest
     ```
   - Ensure all tests pass

6. **Commit Your Changes**
   - Write clear, concise commit messages
   - Reference any related issues in your commit messages

7. **Push and Create a Pull Request**
   - Push your changes to your forked repository
   - Open a pull request to the main repository's `main` branch
   - Fill out the pull request template with details about your changes

Coding Guidelines
----------------

- Follow `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_ style guide
- Use type hints for all new code
- Write docstrings following `Google Style Python Docstrings <https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings>`_
- Keep functions small and focused on a single task
- Write meaningful variable and function names

Report Bugs
----------

Found a bug? Please report it by creating a new issue on our `GitHub Issues <https://github.com/Nsfr750/NFC/issues>`_ page. Include:

1. A clear description of the problem
2. Steps to reproduce the issue
3. Expected behavior
4. Actual behavior
5. Screenshots or error messages if applicable

Feature Requests
---------------

Have an idea for a new feature? We'd love to hear it! Create a new issue on our `GitHub Issues <https://github.com/Nsfr750/NFC/issues>`_ page with:

1. A clear description of the feature
2. The problem it solves
3. Any potential implementation ideas

Code of Conduct
--------------

We are committed to fostering a welcoming and inclusive community. By participating in this project, you agree to abide by our `Code of Conduct <https://github.com/Nsfr750/NFC/CODE_OF_CONDUCT.md>`_.

License
-------

By contributing to NFC Reader/Writer, you agree that your contributions will be licensed under the `GNU General Public License v3.0 <https://www.gnu.org/licenses/gpl-3.0.html>`_.

Thank You!
---------

We appreciate your time and effort in making NFC Reader/Writer better for everyone! Your contributions help improve the tool for users around the world.
