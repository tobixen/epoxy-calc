# Changelog

The format of this file is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

I asked the AI to do a code review and fix some annoyances.  It will be released once it's tested.  Testing will only happen next time I mix epoxy ...

### Added

- Makefile
- Command line option `--min-readings` / `-n` to control minimum readings per measurement (default: 6 for wave compensation, use 1 for stable conditions)
- Undo support: type 'undo' during input to remove the last entered reading
- Outlier warnings: alerts when a reading deviates significantly from previous ones
- Help text at startup and in warnings about undo feature

### Fixed

- `chop_extremes()` no longer mutates the input list (uses `sorted()` instead of in-place `sort()`)
- Graceful error handling when weight doesn't increase instead of crashing with assertion error

## [1.0.10] - 2025-12-20

Those days I'm taking a round over most of my python repositories and brushing them up to "best current practices" with ruff, auto-versioning and auto-publish-to-pypi.

I made this script long ago, and have been using it many times later - without changing anything to it.  Yes, there are for sure annoyances that can be improved, perhaps I should take a round and polish it more before using it next time.  Anyway, it's stable, I won't do major changes to it, so I decided to release it as 1.0.

1.0.10 is the first version to be successfully released on PyPI.

### Changed

- Lifted the project up to "best current practices", aiming for PyPI distribution

### Fixed

- Fixed type comparisons to use `isinstance()` instead of `type() ==`
- Fixed bare `except` clause to catch `ValueError`

### Changed

- Updated README with proper installation instructions (and some minor tweaks to the text)

## [1.0.9] - 2025-12-20 [YANKED]

The observant reader may see that there are many versions missing here, 1.0.8 is not the only "yanked" version.  The pipeline for pushing to pypi didn't work for various reasons, including some name confusions (on my laptop it's located under `~/epoxy` - the command name was `epoxy_calc` - and the github repo was `epoxy_mix_calc`!  What a mess.  Let it be `epoxy_calc`, and only that!)

## [0.0.1] - 2024-01-14

The first revision of the script was made and pushed to github.
