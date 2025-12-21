# TODO-list

* ~~Accept one number instead of six~~ - Done! Use `--min-readings=1` for stable conditions.
* ~~Sometimes wrong numbers are entered~~ - Done! Type 'undo' to remove last entry, and outlier warnings added.
* ~~Too much hard coding~~ - Partially addressed via `--min-readings` option.
* ~~Command line options~~ - Done! Added `--min-readings` / `-n` option.

## Remaining ideas

* Make the number of extremes to chop configurable (currently hardcoded to 2).
* Add `--ratio` option to pre-set the hardener ratio from command line.

## Code review findings (2025-12-21)

Mathematics is sane - the core calculations are correct:
* Trimmed mean approach for noise reduction is statistically sound
* Hardener ratio formula `base * part100 / 100 - hardener` is correct
* Overshoot compensation formula `-hardener_needed / part100 * 100` is correct

~~Minor issues found~~ - All fixed:
* ~~`chop_extremes()` mutates the input list~~ - Fixed: now uses `sorted()` instead of in-place `sort()`.
* ~~`assert mass_added > 0` crashes unfriendly~~ - Fixed: now shows helpful error and allows re-entry.
* Division-by-zero in `avg()` protected by upstream assertions.
