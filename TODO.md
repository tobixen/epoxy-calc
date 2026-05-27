# TODO-list

* Guard rails - if getting numbers that are far off, there should be a warning and/or an "are you sure?"-prompt.
  * The ratio should typically be an integer number between 30 and 100.
  * Weights should *either* be an integer or have one decimal - so if the first number entered is 34.3, then the user is expected to enter 34.0 and not 34.  If the first number entered is 34, then it's unexpected to get 34.4.  Note that if the user say "yes I'm sure" to a prompt, then this should be sticky for the remainder of the session.
  * When entering multiple numbers, a +/- 15% difference may be acceptable (measuring epoxy in heavy waves).  The typical mistake is to enter too few digits or too many digits, or jumping directly from tara to tara+base without hitting enter in between.
* The algorithms would previously chop away a hardcoded number of extreme values (it would neither use median or average, but something in between).  I'm not sure how this was changed now that it's allowable with only one input number, but the algorithm need to be smart on it.
* Add `--ratio` option to pre-set the hardener ratio from command line.
* Make the output easier to read, like on terminals colors or bold/italics can be used to highlight things (does the proposals below make sense?  Are there other ways of doing this?)
  * For the ratio question, keep the current help text, but add a new prompt line with bold "Ratio: "
  * Add a newspace between each section of measurements
  * When base has been added, there is an info section.  Add "total weight" to the info section (even if it's a bit redundant).
  * The important part is the "total weight needed" - make the whole line bold, and also the `{what_needed}`, make that one bold as well.
* Add a first question "what kind of epoxy?" (should also be possible to set this one through `--cli-options`).  It should be allowed to just press enter.
* The script should make a log of what kind of epoxy and how much of it was mixed.
* The script currently exits on  `mass_needed < 0.25`.
  * It should also exit if the user enters "-" on the next reading
  * Relative rather than absolute mass should be used.  If the deviation (`mass_needed/(base+hardener)`) is less than 1% (configurable through command line option), then quit.
  * Probably the accetable deviation should increase for each iteration.  Each iteration adds some more uncertainity, so except in obvious overshoot-scenarioes it doesn't make sense to continue adding small amounts.  But the user will typically decide when "enough is enough".
* (The script was made to measure epoxy in heavy waves, but it's useful also when the readings are completely stable.  The `-n1` ensures it's allowable to enter only one measurement.  However, make another argument making the script expect only one measurement, so that it's not needed to press enter twice) - procrastinate this one a bit
