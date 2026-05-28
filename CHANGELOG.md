# Changelog

The format of this file is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `--ratio` / `-r` option to pre-set the hardener ratio from the command line (skips the ratio prompt)
- `--epoxy-type` / `-e` option and interactive "What kind of epoxy?" question (optional, press Enter to skip)
- `--min-deviation` option: exit threshold as a percentage of total epoxy weight (default 1%), replacing the old hardcoded 0.25g absolute threshold
- `--deviation-factor` option: the exit threshold grows by this factor per correction iteration (default 1.5×), reflecting increasing measurement uncertainty
- `--log-file` option: session log written to `~/.local/share/epoxy-calc/epoxy.log` (timestamp, epoxy type, total weight)
- Input guard rails: warnings when ratio is outside 30–100 or non-integer, when decimal style changes mid-session, or when a reading deviates >15% from the mean — with sticky "yes I'm sure" confirmation
- Output improvements: blank line between sections, current total weight in info block, bold "total weight needed" line with yellow-highlighted weight value, bold "Ratio:" prompt
- Epoxy type and ratio are saved to `~/.config/epoxy-calc/epoxy-types.json` (XDG) after each successful session
- Known epoxy types are prefilled with their saved ratio on the next run (with an accept/decline prompt)
- Tab completion and readline history for the "What kind of epoxy?" prompt (populated from saved types)
- Type "-" at any weight prompt to abort the session cleanly

### Changed

- `find_midpoint()` now scales the number of trimmed extremes to ~20% of the collection size (n//5 per side) instead of always trimming 2 when `min_readings ≥ 6`

## [1.1.0] - 2025-12-21

I asked the AI to do a code review and fix some annoyances.  I've done a quick "dry test", but it will probably be a month until next time I mix epoxy ...

### Added

- Makefile
- Command line option `--min-readings` / `-n` to control minimum readings per measurement (default: 6 for wave compensation, use 1 for stable conditions)
- Undo support: type 'undo' during input to remove the last entered reading
- Outlier warnings: alerts when a reading deviates significantly from previous ones

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
