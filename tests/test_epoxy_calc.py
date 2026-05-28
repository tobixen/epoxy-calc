import pytest
from unittest import mock

from click.testing import CliRunner

from epoxy_calc import (
    avg,
    check_outlier,
    chop_extremes,
    cli,
    find_hardener,
    find_midpoint,
    interactive,
    interactive_read_numbers,
    load_epoxy_types,
    save_epoxy_type,
)


def test_avg():
    assert avg([0, 1, 2, 3, 4]) == 2
    assert avg([3]) == 3
    assert avg([1, 2, 201]) == 68


def test_chop_extremes():
    assert chop_extremes([1, 2, 3, -1000, 1000], 1) == [1, 2, 3]


def test_find_midpoint():
    inputs = [0] * 6
    assert find_midpoint(inputs) == 0
    inputs = [1] * 6
    assert find_midpoint(inputs) == 1
    inputs = [-1, 1] * 3 + [-2, 2]
    assert find_midpoint(inputs) == 0


def test_find_hardener():
    tara = [1] * 6
    base = [101] * 6
    hardener = 0
    what_needed = "hardener"
    part100 = 60
    total_weight = None
    (tara, base, hardener, hardener_needed) = find_hardener(tara, base, hardener, total_weight, what_needed, part100)
    assert tara == 1
    assert base == 100
    assert hardener == 0
    assert hardener_needed == 60

    (tara, base, hardener, hardener_needed) = find_hardener(tara, base, hardener, total_weight, what_needed, part100)

    assert tara == 1
    assert base == 100
    assert hardener == 0
    assert hardener_needed == 60

    total_weight = [111] * 6
    (tara, base, hardener, hardener_needed) = find_hardener(tara, base, hardener, total_weight, what_needed, part100)
    assert tara == 1
    assert base == 100
    assert hardener == 10
    assert hardener_needed == 50


@mock.patch("epoxy_calc.click.prompt")
def test_interactive(prompt):
    # Ratio, Tara, Base, undershoot, overshoot
    input_list = (
        ["60"] + ["0"] * 6 + ["---"] + ["10"] * 6 + ["---"] + ["15"] * 6 + ["---"] + ["17"] * 6 + ["---"] + ["18.7"] * 6 + ["---"]
    )

    def prompt_mocked(text, default=""):
        return input_list.pop(0)

    prompt.side_effect = prompt_mocked

    interactive(epoxy_type="")

    assert not input_list


def test_check_outlier():
    # Not enough values, never an outlier
    assert not check_outlier(100, [])
    assert not check_outlier(100, [1])

    # Normal value within range
    assert not check_outlier(10, [9, 10, 11])

    # Outlier far from mean
    assert check_outlier(100, [9, 10, 11])
    assert check_outlier(-100, [9, 10, 11])


def test_find_midpoint_single_reading():
    # With min_readings=1, just returns the average without trimming
    assert find_midpoint([5], min_readings=1) == 5
    assert find_midpoint([5, 10], min_readings=1) == 7.5
    assert find_midpoint([5, 10, 15], min_readings=3) == 10


def test_find_midpoint_smart_trimming():
    # Small collections (< 5 readings): no trimming
    assert find_midpoint([1, 100], min_readings=1) == 50.5  # 2 readings, no trim
    assert find_midpoint([1, 2, 100], min_readings=1) == pytest.approx(34.33, rel=0.01)

    # 5-9 readings: strip 1 from each end
    # sorted [1,10,10,10,10,100], strip 1: [10,10,10,10], avg=10
    assert find_midpoint([10, 10, 10, 10, 1, 100], min_readings=1) == 10.0

    # 10+ readings: strip 2 from each end
    # sorted [1,1,10,10,10,10,10,10,100,100], strip 2: [10,10,10,10,10,10], avg=10
    assert find_midpoint([10] * 6 + [1, 1, 100, 100], min_readings=1) == 10.0


@mock.patch("epoxy_calc.click.echo")
@mock.patch("epoxy_calc.click.prompt")
def test_interactive_read_numbers_undo(prompt, echo):
    # Use values close together to avoid spread warnings (within 15%)
    # Enter 100, 101, undo (removes 101), 102, ---
    input_list = ["100", "101", "undo", "102", "---"]

    def prompt_mocked(text, default=""):
        return input_list.pop(0)

    prompt.side_effect = prompt_mocked

    result = interactive_read_numbers("test", min_readings=2)
    assert result == [100, 102]


@mock.patch("epoxy_calc.click.prompt")
def test_interactive_single_reading(prompt):
    # Test with min_readings=1 (stable conditions mode)
    input_list = ["60", "0", "---", "10", "---", "16", "---"]

    def prompt_mocked(text, default=""):
        return input_list.pop(0)

    prompt.side_effect = prompt_mocked

    interactive(min_readings=1, epoxy_type="")

    assert not input_list


@mock.patch("epoxy_calc.click.prompt")
def test_deviation_increases_per_iteration(prompt):
    # tara=0, base=100g, 60% ratio -> target hardener = 60g
    # Denominator is now target_hardener (60g), not total epoxy.
    # After correction 1 (153g): hardener=53, need=7; 7/60=11.7% > 1.5% (iter1) -> continue
    # After correction 2 (159g): hardener=59, need=1; 1/60=1.67%
    #   Fixed 1% threshold: 1.67% > 1% -> WOULD continue
    #   iter2 threshold (1%*1.5^2=2.25%): 1.67% < 2.25% -> exits
    # This test consumes exactly the input; if fixed threshold were used, it would IndexError
    input_list = ["60", "0", "---", "100", "---", "153", "---", "159", "---"]

    def prompt_mocked(text, default=""):
        return input_list.pop(0)

    prompt.side_effect = prompt_mocked

    interactive(min_readings=1, epoxy_type="")
    assert not input_list


@mock.patch("epoxy_calc.click.prompt")
def test_denominator_is_target_not_total(prompt):
    # Low ratio (5%): base=1000g, target_hardener=50g
    # After correction 1 (1049g): hardener=49, need=1g
    #   OLD denominator (total=1049): 1/1049=0.095% < 1% -> would exit (wrong!)
    #   NEW denominator (target=50): 1/50=2% > 1% -> correctly continues
    # After correction 2 (1049.4g): hardener=49.4, need=0.6g
    #   NEW: 0.6/50=1.2%; iter2 threshold=1.5% -> 1.2% < 1.5% -> exits
    # If old denominator were used the test would fail (list not consumed at step 2)
    input_list = ["5", "y", "0", "---", "1000", "---", "1049", "---", "1049.4", "---"]

    def prompt_mocked(text, default=""):
        return input_list.pop(0)

    prompt.side_effect = prompt_mocked

    interactive(min_readings=1, epoxy_type="")
    assert not input_list


def test_find_hardener_weight_error():
    # Test that find_hardener returns None when weight doesn't increase
    tara = 1
    base = 100
    hardener = 0
    tot_weight = [100] * 6  # Same as base+tara, no increase
    result = find_hardener(tara, base, hardener, tot_weight, "hardener", 60)
    assert result is None


@mock.patch("epoxy_calc.click.prompt")
def test_relative_threshold_exits(prompt):
    # tara=0, base=1000, 60% ratio -> target_hardener=600g
    # First weight reading: 1599.5g -> hardener=599.5, need=0.5g
    # 0.5 / 600 = 0.083% < 1% default -> should exit
    input_list = ["60", "0", "---", "1000", "---", "1599.5", "---"]

    def prompt_mocked(text, default=""):
        return input_list.pop(0)

    prompt.side_effect = prompt_mocked

    interactive(min_readings=1, epoxy_type="")
    assert not input_list


@mock.patch("epoxy_calc.click.prompt")
def test_relative_threshold_continues(prompt):
    # tara=0, base=100, ratio=60% -> target_hardener=60g, target_base=100g
    # After first add (157g): hardener=57, need=3g; 3/60=5% > 1% -> continues
    # After second add (160.5g): hardener=60.5, overshoot; base_extra=0.833g; 0.833/100=0.833%
    #   iter2 threshold = 1%*1.5^2=2.25% -> 0.833% < 2.25% -> exits
    input_list = ["60", "0", "---", "100", "---", "157", "---", "160.5", "---"]

    def prompt_mocked(text, default=""):
        return input_list.pop(0)

    prompt.side_effect = prompt_mocked

    interactive(min_readings=1, epoxy_type="")
    assert not input_list


def test_validate_ratio_warns():
    from epoxy_calc import validate_ratio
    # No warning for typical integer ratios
    assert validate_ratio(60) is None
    assert validate_ratio(30) is None
    assert validate_ratio(100) is None
    # Warning for out-of-range
    assert validate_ratio(20) is not None
    assert validate_ratio(110) is not None
    # Warning for non-integer
    assert validate_ratio(60.5) is not None


def test_validate_weight_format():
    from epoxy_calc import validate_weight_format
    # No reference -> no warning
    assert validate_weight_format(34.0, []) is None
    # Integer reference, integer value -> fine
    assert validate_weight_format(34, [34, 35]) is None
    # Integer reference, one-decimal value -> warning
    assert validate_weight_format(34.3, [34, 35]) is not None
    # One-decimal reference, one-decimal value -> fine
    assert validate_weight_format(34.3, [34.0, 34.1]) is None
    # One-decimal reference, pure integer -> warning
    assert validate_weight_format(34, [34.0, 34.1]) is not None


def test_validate_spread_warns():
    from epoxy_calc import validate_spread
    # Within 15% of mean -> fine
    assert validate_spread(100, [100, 100, 100]) is None
    assert validate_spread(114, [100, 100, 100]) is None
    # Beyond 15% of mean -> warning
    assert validate_spread(120, [100, 100, 100]) is not None
    assert validate_spread(80, [100, 100, 100]) is not None


@mock.patch("epoxy_calc.click.prompt")
def test_ratio_guardrail_warn_then_proceed(prompt):
    # Ratio 20 is out of range, user gets warned; entering "y" lets them proceed
    # With tara=0, base=100g, 20% ratio: target_hardener=20g
    # Enter 119.9g: hardener=19.9, need=0.1g; 0.1/20=0.5% < 1% -> exits
    input_list = ["20", "y", "0", "---", "100", "---", "119.9", "---"]

    def prompt_mocked(text, default=""):
        return input_list.pop(0)

    prompt.side_effect = prompt_mocked
    interactive(min_readings=1, epoxy_type="")
    assert not input_list


@mock.patch("epoxy_calc.click.prompt")
def test_ratio_guardrail_retry_on_no(prompt):
    # Ratio 20 rejected ("n"), then valid 60 accepted
    # With tara=0, base=100g, 60%: need 60g; enter 160g: hardener=60, need=0 -> exits
    input_list = ["20", "n", "60", "0", "---", "100", "---", "160", "---"]

    def prompt_mocked(text, default=""):
        return input_list.pop(0)

    prompt.side_effect = prompt_mocked
    interactive(min_readings=1, epoxy_type="")
    assert not input_list


def test_epoxy_type_question_and_log(tmp_path):
    from epoxy_calc import interactive
    log_file = tmp_path / "epoxy.log"

    with mock.patch("epoxy_calc.click.prompt") as prompt:
        # epoxy type, ratio, tara, base, hardener weight
        input_list = ["West System 105/205", "60", "0", "---", "100", "---", "160", "---"]

        def prompt_mocked(text, default=""):
            return input_list.pop(0)

        prompt.side_effect = prompt_mocked
        interactive(min_readings=1, log_file=str(log_file))

    assert not input_list
    lines = log_file.read_text().splitlines()
    assert len(lines) == 1, f"Expected 1 log line, got {len(lines)}"
    assert "West System 105/205" in lines[0]
    assert "ratio=60%" in lines[0]
    assert "base=100.0g" in lines[0]
    assert "hardener=60.0g" in lines[0]
    assert "total=160.0g" in lines[0]


def test_epoxy_type_skippable(tmp_path):
    from epoxy_calc import interactive
    log_file = tmp_path / "epoxy.log"

    with mock.patch("epoxy_calc.click.prompt") as prompt:
        # skip epoxy type by pressing enter (empty string), then proceed
        input_list = ["", "60", "0", "---", "100", "---", "160", "---"]

        def prompt_mocked(text, default=""):
            return input_list.pop(0)

        prompt.side_effect = prompt_mocked
        interactive(min_readings=1, log_file=str(log_file))

    assert not input_list


def test_epoxy_type_cli_option():
    runner = CliRunner()
    inputs = "\n".join(["60", "0", "---", "100", "---", "160", "---"]) + "\n"
    result = runner.invoke(cli, ["--min-readings", "1", "--epoxy-type", "Test Epoxy"], input=inputs)
    assert result.exit_code == 0
    assert "Test Epoxy" in result.output


def test_output_formatting_bold_and_total():
    runner = CliRunner()
    # tara=0, base=100g, 60% ratio; enter 160g (adds 60g hardener, done)
    # empty first line skips epoxy-type question
    inputs = "\n".join(["", "60", "0", "---", "100", "---", "160", "---"]) + "\n"
    result = runner.invoke(cli, ["--min-readings", "1"], input=inputs, color=True)
    assert result.exit_code == 0
    # Info section must include current total weight line (tara+base+hardener = 160g)
    assert "total weight:" in result.output
    # Bold "total weight needed" line should be present
    assert "total weight needed:" in result.output


@mock.patch("epoxy_calc.click.prompt")
def test_ratio_cli_option(prompt):
    # --ratio pre-sets the hardener ratio, skipping the ratio question
    input_list = ["0", "---", "10", "---", "16", "---"]

    def prompt_mocked(text, default=""):
        return input_list.pop(0)

    prompt.side_effect = prompt_mocked

    interactive(min_readings=1, ratio=60, epoxy_type="")

    assert not input_list


def test_ratio_cli_flag():
    runner = CliRunner()
    # empty first line skips epoxy-type question
    inputs = "\n".join(["", "0", "---", "10", "---", "16", "---"]) + "\n"
    result = runner.invoke(cli, ["--ratio", "60", "--min-readings", "1"], input=inputs)
    assert result.exit_code == 0


@mock.patch("epoxy_calc.click.prompt")
def test_exit_on_dash(prompt):
    # User enters "-" to abort the session
    input_list = ["60", "0", "---", "10", "---", "-"]

    def prompt_mocked(text, default=""):
        return input_list.pop(0)

    prompt.side_effect = prompt_mocked

    interactive(min_readings=1, epoxy_type="")

    assert not input_list


# --- Config persistence tests ---


def test_load_epoxy_types_missing_file():
    assert load_epoxy_types() == {}


def test_load_epoxy_types_corrupt_file(tmp_path):
    import epoxy_calc
    corrupt = tmp_path / "corrupt.json"
    corrupt.write_text("not valid json{{{")
    with mock.patch("epoxy_calc.CONFIG_FILE", str(corrupt)):
        assert load_epoxy_types() == {}


def test_save_and_load_epoxy_type():
    save_epoxy_type("West System 105/205", 60.0)
    save_epoxy_type("Epifanes", 45.0)
    result = load_epoxy_types()
    assert result == {"West System 105/205": 60.0, "Epifanes": 45.0}


def test_save_epoxy_type_overwrites_ratio():
    save_epoxy_type("West System 105/205", 60.0)
    save_epoxy_type("West System 105/205", 55.0)
    assert load_epoxy_types()["West System 105/205"] == 55.0


@mock.patch("epoxy_calc.click.prompt")
def test_interactive_prefills_known_ratio(prompt, tmp_path):
    save_epoxy_type("West System 105/205", 60.0)
    # epoxy type -> "use saved ratio? y" -> tara -> base -> hardener done
    input_list = ["West System 105/205", "y", "0", "---", "100", "---", "160", "---"]

    def prompt_mocked(text, default=""):
        return input_list.pop(0)

    prompt.side_effect = prompt_mocked
    interactive(min_readings=1, log_file=str(tmp_path / "epoxy.log"))
    assert not input_list


@mock.patch("epoxy_calc.click.prompt")
def test_interactive_can_decline_saved_ratio(prompt, tmp_path):
    save_epoxy_type("West System 105/205", 60.0)
    # decline saved ratio ("n"), then enter a different ratio
    input_list = ["West System 105/205", "n", "45", "0", "---", "100", "---", "145", "---"]

    def prompt_mocked(text, default=""):
        return input_list.pop(0)

    prompt.side_effect = prompt_mocked
    interactive(min_readings=1, log_file=str(tmp_path / "epoxy.log"))
    assert not input_list


@mock.patch("epoxy_calc.click.prompt")
def test_interactive_saves_epoxy_type_after_run(prompt, tmp_path):
    # Unknown type entered; after a successful run it should be saved in config
    input_list = ["NewEpoxy", "60", "0", "---", "100", "---", "160", "---"]

    def prompt_mocked(text, default=""):
        return input_list.pop(0)

    prompt.side_effect = prompt_mocked
    interactive(min_readings=1, log_file=str(tmp_path / "epoxy.log"))
    assert not input_list
    assert load_epoxy_types().get("NewEpoxy") == 60.0


@mock.patch("epoxy_calc.click.prompt")
def test_interactive_unknown_epoxy_type_skips_prefill(prompt, tmp_path):
    # No saved config for this type -> proceeds straight to ratio prompt
    input_list = ["UnknownEpoxy", "60", "0", "---", "100", "---", "160", "---"]

    def prompt_mocked(text, default=""):
        return input_list.pop(0)

    prompt.side_effect = prompt_mocked
    interactive(min_readings=1, log_file=str(tmp_path / "epoxy.log"))
    assert not input_list
