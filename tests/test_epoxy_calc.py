from unittest import mock

from epoxy_calc import (
    avg,
    check_outlier,
    chop_extremes,
    find_hardener,
    find_midpoint,
    interactive,
    interactive_read_numbers,
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

    interactive()

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


@mock.patch("epoxy_calc.click.echo")
@mock.patch("epoxy_calc.click.prompt")
def test_interactive_read_numbers_undo(prompt, echo):
    # Enter 5, 10, undo (removes 10), 15, ---
    input_list = ["5", "10", "undo", "15", "---"]

    def prompt_mocked(text, default=""):
        return input_list.pop(0)

    prompt.side_effect = prompt_mocked

    result = interactive_read_numbers("test", min_readings=2)
    assert result == [5, 15]


@mock.patch("epoxy_calc.click.prompt")
def test_interactive_single_reading(prompt):
    # Test with min_readings=1 (stable conditions mode)
    input_list = ["60", "0", "---", "10", "---", "16", "---"]

    def prompt_mocked(text, default=""):
        return input_list.pop(0)

    prompt.side_effect = prompt_mocked

    interactive(min_readings=1)

    assert not input_list


def test_find_hardener_weight_error():
    # Test that find_hardener returns None when weight doesn't increase
    tara = 1
    base = 100
    hardener = 0
    tot_weight = [100] * 6  # Same as base+tara, no increase
    result = find_hardener(tara, base, hardener, tot_weight, "hardener", 60)
    assert result is None
