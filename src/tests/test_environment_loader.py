"""Env loader tests"""

import pytest
from roguelike.game_engine.env_manager.map import MapCoordinates
from roguelike.game_engine.env_manager.map_objects_storage import Stats, Obstacle
from roguelike.game_engine.game_manager.game_constructor.environment_loader import _load_coordinates, _load_stats, \
    _load_obstacle, _load_treasure, _load_player


def test_coordinates_load_correctly() -> None:
    assert _load_coordinates([0, 1]) == MapCoordinates(0, 1)

    with pytest.raises(ValueError):
        _load_coordinates([])
    with pytest.raises(ValueError):
        _load_coordinates([0])
    with pytest.raises(ValueError):
        _load_coordinates([0, 1, 2])


def test_stats_load_correctly() -> None:
    assert _load_stats({"health": 100.0, "attack": 100.0}) == Stats(health=100.0, attack=100.0)

    with pytest.raises(ValueError):
        _load_stats({})
    with pytest.raises(ValueError):
        _load_stats({"health": 100.0, "attack": 100.0, "defence": 100.0})


def test_obstacle_load_correctly() -> None:
    assert _load_obstacle({}) == Obstacle()

    with pytest.raises(ValueError):
        _load_obstacle({"health": 100.0, "attack": 100.0, "defence": 100.0})


def test_treasure_load_correctly() -> None:
    test_treasure = _load_treasure({"name": "Super Helmet", "stats": {"health": 10.0, "attack": 0.0}})
    assert test_treasure.name == "Super Helmet"
    assert test_treasure.stats == Stats(10.0, 0.0)

    with pytest.raises(ValueError):
        _load_treasure({})
    with pytest.raises(ValueError):
        _load_treasure({"health": 100.0, "attack": 100.0, "defence": 100.0})


def test_player_load_correctly() -> None:
    test_player = _load_player({"stats": {"health": 10.0, "attack": 0.0}})
    assert test_player.stats == Stats(10.0, 0.0)

    with pytest.raises(ValueError):
        _load_player({})
    with pytest.raises(ValueError):
        _load_player({"name": "Super Helmet", "stats": {"health": 10.0, "attack": 0.0}})
