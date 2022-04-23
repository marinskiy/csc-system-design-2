"""Game generator tests"""

import pytest

from roguelike.game_engine.game_manager.game_constructor.game_generator import GameGenerator


def test_random_value_from_range() -> None:
    test_value = GameGenerator._get_random_value_from_range([0, 100])  # pylint: disable=W0212
    assert 0 <= test_value <= 100

    test_value = GameGenerator._get_random_value_from_range([0, 0])  # pylint: disable=W0212
    assert test_value == 0

    with pytest.raises(ValueError):
        GameGenerator._get_random_value_from_range([100, 0])  # pylint: disable=W0212


def test_decide_from_probability() -> None:
    assert not GameGenerator._decide_from_probability(0)  # pylint: disable=W0212
    assert GameGenerator._decide_from_probability(1)  # pylint: disable=W0212


def test_generate_map() -> None:
    test_map = GameGenerator._generate_map({"width": [30, 100], "height": [1, 10]})  # pylint: disable=W0212+

    assert 30 <= test_map._width <= 100  # pylint: disable=W0212+
    assert 1 <= test_map._height <= 10  # pylint: disable=W0212+

    with pytest.raises(ValueError):
        GameGenerator._generate_map({"width": [0, 0], "height": [1, 10]})  # pylint: disable=W0212
    with pytest.raises(ValueError):
        GameGenerator._generate_map({"width": [30, 100], "height": [0, 0]})  # pylint: disable=W0212
