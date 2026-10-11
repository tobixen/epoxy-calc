"""Swell-resistant epoxy mix calculator.

A tool to help calculate the correct ratio of epoxy base and hardener,
compensating for measurement inaccuracies by using multiple measurements.
"""

import datetime
import json
import os

import click

try:
    import readline as _readline
    _HAS_READLINE = True
except ImportError:
    _HAS_READLINE = False

_XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
CONFIG_FILE = os.path.join(_XDG_CONFIG_HOME, "epoxy-calc", "epoxy-types.json")


def load_epoxy_types() -> dict:
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_epoxy_type(name: str, ratio: float) -> None:
    config = load_epoxy_types()
    config[name] = ratio
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def avg(coll):
    return sum(coll) / len(coll)


def chop_extremes(coll, strip_num):
    coll = sorted(coll)
    return coll[strip_num:-strip_num]


def find_midpoint(coll, min_readings=6):
    """Calculate a stable midpoint from multiple readings.

    Trims ~20% of extremes from each end, scaled to collection size:
    - <5 readings: no trimming (simple average)
    - 5-9 readings: strip 1 from each end
    - 10-14 readings: strip 2, etc.
    """
    strip_num = len(coll) // 5
    if strip_num > 0:
        coll = chop_extremes(coll, strip_num)
    return avg(coll)


def find_hardener(tara, base, hardener, tot_weight, adding, part100, min_readings=6):
    if isinstance(tara, list):
        tara = find_midpoint(tara, min_readings)
    if isinstance(base, list):
        base = find_midpoint(base, min_readings) - tara
    if isinstance(tot_weight, list):
        tot_weight = find_midpoint(tot_weight, min_readings)
        mass_added = tot_weight - base - tara - hardener
        if mass_added <= 0:
            click.echo(f"Error: Weight didn't increase (expected > {base + tara + hardener:.1f}g, got {tot_weight:.1f}g)")
            click.echo("Please check your measurements and try again.")
            return None
        click.echo(f"New {adding} added: {mass_added:.1f}g")
        if adding == "hardener":
            hardener += mass_added
        elif adding == "base":
            base += mass_added
    hardener_needed = base * part100 / 100 - hardener
    click.echo("")
    click.echo(f"tara: {tara:.1f}g")
    click.echo(f"base: {base:.1f}g")
    click.echo(f"hardener: {hardener:.1f}g")
    click.echo(f"total weight: {tara + base + hardener:.1f}g")
    click.echo(f"more hardener needed: {hardener_needed:.1f}g")
    total_needed = tara + base + hardener + max(hardener_needed, -hardener_needed / part100 * 100)
    what_needed = "hardener" if hardener_needed >= 0 else "base"
    click.echo(
        click.style("total weight needed: ", bold=True)
        + click.style(f"{total_needed:.1f}g", bold=True, fg="yellow")
        + click.style(f" ({what_needed})", bold=True)
    )
    return (tara, base, hardener, hardener_needed)


def validate_ratio(ratio):
    """Return a warning string if ratio is suspicious, else None."""
    if ratio != int(ratio):
        return f"Ratio {ratio} is not an integer. Typical ratios are whole numbers between 30 and 100."
    if not (30 <= ratio <= 100):
        return f"Ratio {ratio} is outside the typical range (30–100). Double-check your product datasheet."
    return None


def _is_integer_style(value):
    """Return True if value was typed without a decimal part.

    For a string the typed text decides, so "34.0" is decimal style.
    """
    if isinstance(value, str):
        return "." not in value and "," not in value
    return value == int(value)


def validate_weight_format(value, existing_values):
    """Return a warning string if value uses a different decimal style than existing values, else None."""
    if not existing_values:
        return None
    ref_is_integer = all(_is_integer_style(v) for v in existing_values)
    value_is_integer = _is_integer_style(value)
    if ref_is_integer and not value_is_integer:
        return f"{value} has a decimal part but previous readings were integers. Did you mistype?"
    if not ref_is_integer and value_is_integer:
        return f"{value} looks like an integer but previous readings had decimals (e.g. {existing_values[0]}). Did you mistype?"
    return None


def validate_spread(value, existing_values, tolerance=0.15):
    """Return a warning string if value deviates more than tolerance from the mean, else None."""
    if not existing_values:
        return None
    mean = avg(existing_values)
    if mean == 0:
        return None
    deviation = abs(value - mean) / abs(mean)
    if deviation > tolerance:
        return f"{value} deviates {deviation*100:.0f}% from the mean ({mean:.1f}), which exceeds the ±{tolerance*100:.0f}% threshold."
    return None


def check_outlier(value, existing_values, threshold=3.0):
    """Check if a value is an outlier compared to existing values.

    Returns True if the value deviates more than threshold from the mean,
    relative to the range of existing values.
    """
    if len(existing_values) < 2:
        return False
    mean = avg(existing_values)
    value_range = max(existing_values) - min(existing_values)
    if value_range < 0.5:  # If values are very close, use absolute threshold
        value_range = 1.0
    deviation = abs(value - mean)
    return deviation > value_range * threshold


def interactive_read_numbers(what, min_readings=6, confirmed_ok=None):
    """Read multiple measurements interactively.

    confirmed_ok: mutable set of warning type tags the user has already confirmed OK
    (sticky across readings within the session).
    """
    if confirmed_ok is None:
        confirmed_ok = set()
    ret = []
    typed = []  # the readings as typed, for the decimal-style check
    while True:
        number = click.prompt(f"Enter {what}", default="---")
        if number == "---":
            if len(ret) < min_readings:
                click.echo(f"At least {min_readings} reading(s) needed!")
                continue
            break
        if number == "-":
            return None
        if number.lower() == "undo":
            if ret:
                removed = ret.pop()
                typed.pop()
                click.echo(f"Removed {removed:.1f}. {len(ret)} reading(s) remaining.")
            else:
                click.echo("Nothing to undo.")
            continue
        raw = number.strip()
        try:
            number = float(raw)
        except ValueError:
            click.echo("Not a number! Try again (or type 'undo' to remove last entry)")
            continue
        checks = [
            ("format", validate_weight_format(raw, typed)),
            ("spread", validate_spread(number, ret)),
        ]
        discard = False
        for tag, warning in checks:
            if warning and tag not in confirmed_ok:
                click.echo(f"Warning: {warning}")
                answer = click.prompt("Are you sure? (y/n)", default="n")
                if answer.lower() != "y":
                    click.echo("Discarding reading. Try again.")
                    discard = True
                    break
                confirmed_ok.add(tag)
        if discard:
            continue
        if check_outlier(number, ret):
            click.echo(f"Warning: {number} seems quite different from previous readings. Type 'undo' to remove it.")
        ret.append(number)
        typed.append(raw)
    return ret


DEFAULT_LOG_FILE = os.path.expanduser("~/.local/share/epoxy-calc/epoxy.log")


def write_log(log_file, epoxy_type, tara, base, hardener, part100):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    epoxy_label = epoxy_type if epoxy_type else "(unspecified)"
    total = tara + base + hardener
    try:
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        with open(log_file, "a") as f:
            f.write(
                f"{timestamp}  {epoxy_label}  ratio={part100:g}%"
                f"  tara={tara:.1f}g  base={base:.1f}g  hardener={hardener:.1f}g  total={total:.1f}g\n"
            )
    except OSError as e:
        click.echo(f"Could not write the log file {log_file}: {e}")


def _finish(log_file, epoxy_type, tara, base, hardener, part100):
    """Log the mix and remember the epoxy type's ratio."""
    write_log(log_file, epoxy_type, tara, base, hardener, part100)
    if epoxy_type:
        try:
            save_epoxy_type(epoxy_type, part100)
        except OSError as e:
            click.echo(f"Could not save the ratio for {epoxy_type}: {e}")


def _prompt_epoxy_type(known_types: dict) -> str:
    """Prompt for epoxy type with tab completion and readline history from known types."""
    if _HAS_READLINE:
        orig_completer = _readline.get_completer()
        orig_delims = _readline.get_completer_delims()
        type_names = list(known_types.keys())

        def _completer(text, state):
            matches = [n for n in type_names if n.lower().startswith(text.lower())]
            return matches[state] if state < len(matches) else None

        for name in reversed(type_names):
            _readline.add_history(name)
        _readline.set_completer(_completer)
        _readline.set_completer_delims("")
        _readline.parse_and_bind("tab: complete")
        try:
            return click.prompt("What kind of epoxy?", default="") or None
        finally:
            _readline.set_completer(orig_completer)
            _readline.set_completer_delims(orig_delims)
    return click.prompt("What kind of epoxy?", default="") or None


def interactive(min_readings=6, ratio=None, min_deviation=1.0, deviation_factor=1.5, epoxy_type=None, log_file=None):
    if log_file is None:
        log_file = DEFAULT_LOG_FILE
    click.echo("Tip: Type 'undo' to remove the last entered reading.")
    confirmed_ok: set = set()
    known_types = load_epoxy_types()
    if epoxy_type is None:
        epoxy_type = _prompt_epoxy_type(known_types)
    if epoxy_type:
        click.echo(f"Epoxy type: {epoxy_type}")
    part100 = None
    if ratio is not None:
        part100 = float(ratio)
        if part100 <= 0:
            raise click.BadParameter("the ratio must be positive", param_hint="--ratio")
        warning = validate_ratio(part100)
        if warning:
            click.echo(f"Warning: {warning}")
        click.echo(f"Hardener ratio: {part100:g}g per 100g base (preset)")
    elif epoxy_type and epoxy_type in known_types:
        saved_ratio = known_types[epoxy_type]
        click.echo(f"Known ratio for {epoxy_type}: {saved_ratio:g}g per 100g base")
        answer = click.prompt("Use this ratio? (y/n)", default="y")
        if answer.lower() == "y":
            part100 = saved_ratio
    if part100 is None:
        while True:
            click.echo("How many grams of hardener is needed for 100g of base?")
            try:
                part100 = float(click.prompt(click.style("Ratio", bold=True)))
            except ValueError:
                click.echo("Not a number! Try again.")
                continue
            if part100 <= 0:
                click.echo("The ratio must be positive. Try again.")
                continue
            warning = validate_ratio(part100)
            if warning and "ratio" not in confirmed_ok:
                click.echo(f"Warning: {warning}")
                answer = click.prompt("Are you sure? (y/n)", default="n")
                if answer.lower() != "y":
                    continue
                confirmed_ok.add("ratio")
            break
    if min_readings >= 6:
        click.echo("Measure the tara. Enter the observed tara at least six times.")
    else:
        click.echo("Measure the tara.")
    tara = interactive_read_numbers("tara", min_readings, confirmed_ok=confirmed_ok)
    if tara is None:
        return
    if min_readings >= 6:
        click.echo("Add base and enter the observed total weight at least six times.")
    else:
        click.echo("Add base and enter the total weight.")
    base = interactive_read_numbers("total weight base+tara", min_readings, confirmed_ok=confirmed_ok)
    if base is None:
        return
    # From here on base is in the cup: "-" means "enough now", so the
    # mix as last measured is logged.  Ctrl-C (click.Abort) logs nothing.
    hardener = 0
    what_needed = "hardener"
    total_weight = None
    correction_count = 0
    last = None

    def _finish_last():
        if last is not None:
            _finish(log_file, epoxy_type, *last, part100)

    while True:
        result = find_hardener(tara, base, hardener, total_weight, what_needed, part100, min_readings)
        if result is None:
            # Error in measurement, ask for re-entry
            total_weight = interactive_read_numbers(
                f"total weight tara+base+hardener after adding {what_needed}", min_readings, confirmed_ok=confirmed_ok
            )
            if total_weight is None:
                _finish_last()
                return
            # The re-entry replaces the bad reading, which was already
            # counted: not another correction
            continue
        (tara, base, hardener, hardener_needed) = result
        last = (tara, base, hardener)
        if hardener_needed < 0:
            what_needed = "base"
            mass_needed = -hardener_needed / part100 * 100
            target_amount = base
        else:
            what_needed = "hardener"
            mass_needed = hardener_needed
            target_amount = base * part100 / 100
        current_threshold = min_deviation * (deviation_factor ** correction_count)
        if target_amount > 0 and mass_needed / target_amount < current_threshold / 100:
            _finish(log_file, epoxy_type, tara, base, hardener, part100)
            return
        if min_readings >= 6:
            click.echo(f"Try to add {mass_needed:.1f}g {what_needed}. Enter the observed total weight at least six times.")
        else:
            click.echo(f"Try to add {mass_needed:.1f}g {what_needed}. Enter the total weight.")
        total_weight = interactive_read_numbers(
            f"total weight tara+base+hardener after adding {what_needed}", min_readings, confirmed_ok=confirmed_ok
        )
        if total_weight is None:
            _finish_last()
            return
        correction_count += 1


@click.command()
@click.option(
    "--min-readings", "-n",
    default=6,
    help="Minimum readings per measurement (default: 6 for wave compensation, use 1 for stable conditions)."
)
@click.option(
    "--ratio", "-r",
    default=None,
    type=float,
    help="Hardener ratio: grams of hardener per 100g of base (skips the ratio prompt)."
)
@click.option(
    "--min-deviation",
    default=1.0,
    type=float,
    show_default=True,
    help="Stop when the remaining mass needed is below this percentage of the target amount of the component being added."
)
@click.option(
    "--deviation-factor",
    default=1.5,
    type=float,
    show_default=True,
    help="Multiply the deviation threshold by this factor after each correction iteration."
)
@click.option(
    "--epoxy-type", "-e",
    default=None,
    help="Epoxy product name/type (skips the epoxy-type prompt and used in the log)."
)
@click.option(
    "--log-file",
    default=None,
    help=f"Path to log file (default: {DEFAULT_LOG_FILE})."
)
def cli(min_readings, ratio, min_deviation, deviation_factor, epoxy_type, log_file):
    """Interactive epoxy mix calculator.

    On a boat with waves, use the default of 6 readings per measurement
    to filter out wave-induced fluctuations.

    On stable ground, use --min-readings=1 for quick single measurements.
    """
    interactive(
        min_readings, ratio=ratio, min_deviation=min_deviation, deviation_factor=deviation_factor,
        epoxy_type=epoxy_type, log_file=log_file
    )


if __name__ == "__main__":
    cli()
