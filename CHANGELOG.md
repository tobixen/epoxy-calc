# Changelog

The format of this file is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-12-20

### Changed

- Lifted the project up to "best current practices", aiming for PyPI distribtion

### Fixed

- Fixed type comparisons to use `isinstance()` instead of `type() ==`
- Fixed bare `except` clause to catch `ValueError`

## [0.0.1] - 2024-01-14

### Added

- Initial release
- Interactive CLI for calculating epoxy base/hardener ratios
- Swell-resistant measurement system using multiple readings to find midpoint
- Automatic correction when too much hardener or base is added
