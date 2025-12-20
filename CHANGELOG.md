# Changelog

The format of this file is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Modernized package structure for PyPI distribution
- Converted to proper Python package structure (epoxy_calc/)
- Added pyproject.toml with Poetry and poetry-dynamic-versioning
- Added ruff linting configuration
- Added pre-commit hooks for code quality
- Added GitHub Actions CI workflow (Python 3.9-3.13)
- Added GitHub Actions PyPI publish workflow with trusted publishing
- Moved tests to tests/ directory

### Fixed

- Fixed type comparisons to use `isinstance()` instead of `type() ==`
- Fixed bare `except` clause to catch `ValueError`

## [0.0.1] - 2024-01-14

### Added

- Initial release
- Interactive CLI for calculating epoxy base/hardener ratios
- Swell-resistant measurement system using multiple readings to find midpoint
- Automatic correction when too much hardener or base is added
