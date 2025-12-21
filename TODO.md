# TODO-list

* Accept one number instead of six.  This script was initially written to solve the wave problem, but it's useful also for solving calculation and overshoot problems when being on the hard or being on completely flat water.
* Sometimes wrong numbers are entered, it's needed to have some possibilities to undo or edit old numbers. (and perhaps some kind of warnings when numbers deviate very much from the previous numbers)
* Too much hard coding in the project - ilke how many of the "extremes" should be chopped off.
* Command line options.  I've imported the `click`-library for this purpose, but I only use it for creating prompts and output.

## Code review findings (2025-12-21)

Mathematics is sane - the core calculations are correct:
* Trimmed mean approach for noise reduction is statistically sound
* Hardener ratio formula `base * part100 / 100 - hardener` is correct
* Overshoot compensation formula `-hardener_needed / part100 * 100` is correct

Minor issues found:
* `chop_extremes()` mutates the input list via in-place `sort()` - not causing bugs currently since lists aren't reused, but is a side-effect code smell. Consider `sorted(coll)` instead.
* `assert mass_added > 0` (line 33) crashes unfriendly if user enters a total weight that doesn't increase (e.g., typo or weighing error). Could benefit from better error handling.
* No explicit handling of division-by-zero in `avg()`, though this is protected upstream by the `assert len(coll) >= 6` in `find_midpoint()`.
