# Changelog

The format of this file is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.3] - 2025-12-20

Those days I'm taking a round over most of my python repositories and brushing them up to "best current practices" with ruff, auto-versioning and auto-publish-to-pypi.

I made this script long ago, and have been using it many times later - without changing anything to it.  Yes, there are for sure annoyances that can be improved, perhaps I should take a round and polish it more before using it next time.  Anyway, it's stable, I won't do major changes to it, so I decided to release it as 1.0.

### Changed

- Lifted the project up to "best current practices", aiming for PyPI distribtion

### Fixed

- Fixed type comparisons to use `isinstance()` instead of `type() ==`
- Fixed bare `except` clause to catch `ValueError`

## [1.0.2] - 2025-12-20 [YANKED]

"Do not release things in the middle of the night" I told myself long time ago.

## [1.0.1] - 2025-12-20 [YANKED]

Yanked, because the pypi publish pipeline failed due to project name confusion.  On my laptop it's located under `~/epoxy` - the command name was `epoxy_calc` - and the github repo was `epoxy_mix_calc`!  What a mess.  Let it be `epoxy_calc`, and only that!

## [1.0.0] - 2025-12-20 [YANKED]

Yanked, because the CHANGELOG wasn't updated, and because the pypi publish pipeline failed due to project name confusion.

## [0.0.1] - 2024-01-14

### Added

- Initial release
- Interactive CLI for calculating epoxy base/hardener ratios
- Swell-resistant measurement system using multiple readings to find midpoint
- Automatic correction when too much hardener or base is added
