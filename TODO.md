# TODO-list

* (The script was made to measure epoxy in heavy waves, but it's useful also when the readings are completely stable.  The `-n1` ensures it's allowable to enter only one measurement.  However, make another argument making the script expect only one measurement, so that it's not needed to press enter twice) - procrastinate this one a bit

## Leftovers from the 2026-10-11 review

* Config file robustness: a corrupt epoxy-types.json loads as {} and the
  next save overwrites every saved type; non-dict JSON or a non-numeric
  ratio crashes; the write is not atomic (temp file + os.replace).
* `total_epoxy` was dead code (removed); `find_midpoint`'s `min_readings`
  parameter is now unused, and with 6 readings it trims 1 per side instead
  of 2 — decide whether that is the intended outlier rejection.
* `XDG_CONFIG_HOME=""` should count as unset; the log file ignores
  `XDG_DATA_HOME`.
* The epoxy-type prompt adds names to the global readline history (they
  show up on arrow-up in the numeric prompts); the completer is
  case-insensitive but the known-type lookup is case-sensitive; no test
  for completion.
* README.md does not mention `--ratio`, `--epoxy-type`, `--log-file`,
  `--min-deviation`, `--deviation-factor`, the config file or the log.
