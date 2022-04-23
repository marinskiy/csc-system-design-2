"""Game generator tests"""

import pytest

from roguelike.game_engine.env_manager.map import MapCoordinates
from roguelike.game_engine.env_manager.map_objects_storage import Obstacle
from roguelike.game_engine.game_manager.game_constructor.game_generator import GameGenerator, StatsGenerator, \
    PlayerCharacterGenerator, ObstacleGenerator, TreasureGenerator, MapObjectGenerator, \
    MapObjectWheel, MapGenerator, get_random_int_from_range, get_random_float_from_range


def test_random_value_from_range() -> None:
    test_value = get_random_int_from_range([0, 100])
    assert 0 <= test_value <= 100

    test_value = get_random_float_from_range([0.1, 0.5])
    assert 0.1 <= test_value <= 0.5

    test_value = get_random_int_from_range([0, 0])
    assert test_value == 0

    with pytest.raises(ValueError):
        get_random_int_from_range([100, 0])
    with pytest.raises(ValueError):
        get_random_float_from_range([0.5, 0.1])


def test_stats_generated_correctly() -> None:
    test_stats = StatsGenerator({"health": [100.0, 150.0], "attack": [10.0, 20.0]}).generate()

    assert 100.0 <= test_stats.health <= 150.0
    assert 10.0 <= test_stats.attack <= 20.0

    with pytest.raises(ValueError):
        StatsGenerator({})
    with pytest.raises(ValueError):
        StatsGenerator({"health": [100.0, 110.0], "attack": [100.0, 150.0], "defence": [100.0, 200.0]})


def test_player_generated_correctly() -> None:
    test_player = PlayerCharacterGenerator(  # pylint: disable=W0212
        {"stats": {"health": [10.0, 20.0], "attack": [0.0, 100]}}).generate()

    assert 10.0 <= test_player.stats.health <= 20.0
    assert 0.0 <= test_player.stats.attack <= 100.0

    with pytest.raises(ValueError):
        PlayerCharacterGenerator({})
    with pytest.raises(ValueError):
        PlayerCharacterGenerator(
            {"name": "Super Helmet", "stats": {"health": [10.0, 20.0], "attack": [0.0, 100]}})


def test_obstacle_generated_correctly() -> None:
    assert ObstacleGenerator({}).generate() == Obstacle()

    with pytest.raises(ValueError):
        ObstacleGenerator({"health": 100.0, "attack": 100.0, "defence": 100.0})


def test_treasure_generated_correctly() -> None:
    test_treasure = TreasureGenerator(
        {"names": ["Helmet", "Boots"], "stats": {"health": [10.0, 20.0], "attack": [0.0, 30]}}).generate()
    assert test_treasure.name in ["Helmet", "Boots"]
    assert 10.0 <= test_treasure.stats.health <= 20.0

    with pytest.raises(ValueError):
        TreasureGenerator({})
    with pytest.raises(ValueError):
        TreasureGenerator({"health": 100.0, "attack": 100.0, "defence": 100.0})


def test_map_object_generated_correctly() -> None:
    object_generator = MapObjectGenerator(
        {"player": {"stats": {"health": [90.0, 110.0], "attack": [90.0, 110.0]}}, "obstacle": {},
         "treasure": {"names": ["helmet", "boots", "armor"], "stats": {"health": [-10, 30], "attack": [-10, 30]}}
         }
    )

    test_player = object_generator.generate("player")
    assert 90.0 <= test_player.stats.health <= 110.0
    assert 90.0 <= test_player.stats.attack <= 110.0

    test_obstacle = object_generator.generate("obstacle")
    assert test_obstacle == Obstacle()

    test_treasure = object_generator.generate("treasure")
    assert test_treasure.name in ["helmet", "boots", "armor"]
    assert -10 <= test_treasure.stats.health <= 30.0
    assert -10 <= test_treasure.stats.attack <= 30.0

    with pytest.raises(ValueError):
        object_generator.generate("none")


def test_wheel() -> None:
    wheel = MapObjectWheel({"population": ["obstacle", "treasure", "none"], "weights": [10, 5, 85]})
    assert wheel.get_next_object_type() in ["obstacle", "treasure", "none"]

    wheel = MapObjectWheel({"population": ["obstacle", "treasure", "none"], "weights": [100, 0, 0]})
    assert wheel.get_next_object_type() == "obstacle"

    with pytest.raises(ValueError):
        MapObjectWheel({})
    with pytest.raises(ValueError):
        MapObjectWheel({"population": ["obstacle", "treasure", "none"], "weights": [100, 0, 0, 10]})


def test_map_generated_correctly() -> None:
    test_map = MapGenerator({"width": [30, 100], "height": [1, 10]}).generate()

    assert 30 <= test_map.get_width() <= 100
    assert 1 <= test_map.get_height() <= 10


def test_game_state_generated_correctly() -> None:
    state = GameGenerator().generate()

    assert 30 <= state.environment.map.get_width() <= 100
    assert 30 <= state.environment.map.get_height() <= 100

    for i in range(state.environment.map.get_width()):
        for j in range(state.environment.map.get_height()):
            assert len(state.environment.map.get_objects(MapCoordinates(i, j))) <= 1
