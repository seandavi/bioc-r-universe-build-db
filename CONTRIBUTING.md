# Contributing to Bioconductor R-Universe Build Tracker

Thank you for your interest in contributing to the Bioconductor R-Universe Build Tracker! This document provides guidelines and information to help you contribute effectively.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style and Standards](#code-style-and-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)
- [Questions and Support](#questions-and-support)

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow. By participating, you are expected to uphold this standard of behavior. Please be respectful, inclusive, and considerate in all interactions.

## How Can I Contribute?

There are many ways to contribute to this project:

- **Report bugs** - Help us identify and fix issues
- **Suggest enhancements** - Propose new features or improvements
- **Improve documentation** - Fix typos, clarify instructions, or add examples
- **Submit code changes** - Fix bugs or implement new features
- **Review pull requests** - Help review and test changes from other contributors

## Getting Started

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) - Fast Python package installer and resolver
- Git for version control

### Setting Up Your Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/bioc-r-universe-build-db.git
   cd bioc-r-universe-build-db
   ```

3. **Add the upstream repository**:
   ```bash
   git remote add upstream https://github.com/seandavi/bioc-r-universe-build-db.git
   ```

4. **Install dependencies**:
   ```bash
   uv sync
   ```

5. **Verify the installation**:
   ```bash
   uv run bioc-tracker --help
   ```

## Development Workflow

### Creating a Branch

Always create a new branch for your work:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

Use descriptive branch names:
- `feature/` for new features
- `fix/` for bug fixes
- `docs/` for documentation changes
- `refactor/` for code refactoring

### Making Changes

1. Make your changes in your branch
2. Test your changes thoroughly
3. Keep commits focused and atomic
4. Write clear, descriptive commit messages

### Keeping Your Branch Up to Date

Regularly sync with the upstream repository:

```bash
git fetch upstream
git rebase upstream/main
```

## Code Style and Standards

### Python Code Style

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and modular
- Use type hints where appropriate

### Code Organization

- Place new features in appropriate modules within `bioc_build_tracker/`
- Keep related functionality together
- Maintain separation of concerns

### Documentation

- Update the README.md if you change user-facing functionality
- Add docstrings to new functions and classes
- Update inline comments when changing complex code
- Keep documentation clear and concise

## Testing

### Running Tests

Before submitting changes, ensure your code works correctly:

1. **Test basic functionality**:
   ```bash
   uv run bioc-tracker status
   ```

2. **Test with dry-run mode**:
   ```bash
   uv run bioc-tracker sync --dry-run
   uv run bioc-tracker backfill --limit 5 --dry-run
   ```

3. **Test with verbose output**:
   ```bash
   uv run bioc-tracker sync --verbose
   ```

### Manual Testing

- Test commands with various options and edge cases
- Verify error handling with invalid inputs
- Check that data is stored correctly in the expected format

## Submitting Changes

### Pull Request Process

1. **Ensure your code is ready**:
   - All tests pass
   - Code follows style guidelines
   - Documentation is updated
   - Commits are clean and well-described

2. **Push your branch** to your fork:
   ```bash
   git push origin your-branch-name
   ```

3. **Create a pull request** on GitHub:
   - Use a clear, descriptive title
   - Describe what changes you made and why
   - Reference any related issues (e.g., "Fixes #123")
   - Explain how you tested the changes

4. **Address review feedback**:
   - Be responsive to comments
   - Make requested changes
   - Push updates to the same branch

### Pull Request Guidelines

- **Keep PRs focused** - One feature or fix per PR
- **Provide context** - Explain the problem and your solution
- **Include examples** - Show how to use new features
- **Be patient** - Reviews may take time
- **Be open to feedback** - Suggestions help improve the code

## Reporting Bugs

### Before Submitting a Bug Report

- Check the existing issues to avoid duplicates
- Verify the bug exists in the latest version
- Collect information about your environment

### How to Submit a Bug Report

Create an issue on GitHub with:

1. **A clear, descriptive title**
2. **Steps to reproduce** the bug
3. **Expected behavior** - What you expected to happen
4. **Actual behavior** - What actually happened
5. **Environment details**:
   - Python version (`python --version`)
   - Operating system
   - Relevant package versions
6. **Additional context** - Error messages, logs, screenshots

### Bug Report Template

```markdown
**Description**
A clear description of the bug.

**To Reproduce**
1. Run command '...'
2. With options '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., Ubuntu 22.04, macOS 14.0, Windows 11]
- Python version: [e.g., 3.11.5]
- Package version: [e.g., 0.1.0]

**Additional Context**
Any other relevant information.
```

## Suggesting Enhancements

We welcome suggestions for new features and improvements!

### Before Submitting an Enhancement

- Check if the feature already exists
- Check if someone else has suggested it
- Consider if it fits the project's scope

### How to Submit an Enhancement

Create an issue on GitHub with:

1. **A clear, descriptive title**
2. **Use case** - Why is this enhancement needed?
3. **Proposed solution** - How should it work?
4. **Alternatives** - Other approaches you considered
5. **Additional context** - Examples, mockups, or references

## Questions and Support

- **GitHub Issues** - For bug reports and feature requests
- **GitHub Discussions** - For questions and general discussion (if enabled)
- **Project Repository** - Check the README.md for documentation

## Recognition

All contributors will be recognized for their contributions. Thank you for helping make this project better!

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License, the same license as the project.
