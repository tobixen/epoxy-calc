from unittest import mock

from epoxy_calc import avg, chop_extremes, find_hardener, find_midpoint, interactive


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
