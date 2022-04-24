"""Game generator tests"""

import pytest

from roguelike.game_engine.env_manager.enemies import Mob
from roguelike.game_engine.env_manager.map import MapCoordinates
from roguelike.game_engine.env_manager.map_objects_storage import Obstacle, PlayerCharacter, Treasure
from roguelike.game_engine.game_manager.game_constructor.game_generator import GameGenerator, StatsGenerator, \
    PlayerCharacterGenerator, ObstacleGenerator, TreasureGenerator, MapObjectGenerator, \
    MapObjectWheel, MapGenerator, get_random_int_from_range, MobGenerator, MOB_STATS_INCREASE_PER_LEVEL


def test_random_value_from_range() -> None:
    test_int_value = get_random_int_from_range([0, 100])
    assert 0 <= test_int_value <= 100

    test_int_value = get_random_int_from_range([0, 0])
    assert test_int_value == 0

    with pytest.raises(ValueError):
        get_random_int_from_range([100, 0])


def test_stats_generated_correctly() -> None:
    test_stats = StatsGenerator({"health": [100, 150], "attack": [10, 20]}).generate()

    assert 100.0 <= test_stats.health <= 150.0
    assert 10.0 <= test_stats.attack <= 20.0

    with pytest.raises(ValueError):
        StatsGenerator({})
    with pytest.raises(ValueError):
        StatsGenerator({"health": [100, 110], "attack": [100, 150], "defence": [100, 200]})


def test_player_generated_correctly() -> None:
    test_player = PlayerCharacterGenerator(  # pylint: disable=W0212
        {"stats": {"health": [10, 20], "attack": [0, 100]}}).generate()

    assert 10 <= test_player.stats.health <= 20
    assert 0 <= test_player.stats.attack <= 100

    with pytest.raises(ValueError):
        PlayerCharacterGenerator({})
    with pytest.raises(ValueError):
        PlayerCharacterGenerator(
            {"name": "Super Helmet", "stats": {"health": [10, 20], "attack": [0, 100]}})


def test_obstacle_generated_correctly() -> None:
    assert isinstance(ObstacleGenerator({}).generate(), Obstacle)

    with pytest.raises(ValueError):
        ObstacleGenerator({"health": 100, "attack": 100, "defence": 100})


def test_treasure_generated_correctly() -> None:
    test_treasure = TreasureGenerator(
        {"names": ["Helmet", "Boots"], "stats": {"health": [10, 20], "attack": [0, 30]}}).generate()
    assert test_treasure.name in ["Helmet", "Boots"]
    assert 10 <= test_treasure.stats.health <= 20

    with pytest.raises(ValueError):
        TreasureGenerator({})
    with pytest.raises(ValueError):
        TreasureGenerator({"health": 100, "attack": 100, "defence": 100})


def apply_level_multiplier(value: int, level: int) -> int:
    return int(value * (1 + MOB_STATS_INCREASE_PER_LEVEL * level))


def test_mob_generated_correctly() -> None:
    test_mob = MobGenerator({
        "level": [1, 5],
        "radius": [5, 10],
        "behaviours": ["aggressive", "cowardly", "passive"],
        "stats": {"health": [25, 50], "attack": [25, 50]}
    }).generate()

    assert 1 <= test_mob.level <= 5
    assert 5 <= test_mob.action_radius <= 10
    assert apply_level_multiplier(25, test_mob.level) <= test_mob.stats.health <= apply_level_multiplier(50,
                                                                                                         test_mob.level)
    assert apply_level_multiplier(25, test_mob.level) <= test_mob.stats.attack <= apply_level_multiplier(50,
                                                                                                         test_mob.level)


def test_map_object_generated_correctly() -> None:
    object_generator = MapObjectGenerator(
        {
            "player": {"stats": {"health": [90, 110], "attack": [90, 110]}},
            "obstacle": {},
            "treasure": {"names": ["helmet", "boots", "armor"], "stats": {"health": [-10, 30], "attack": [-10, 30]}},
            "mob": {"level": [1, 5], "radius": [5, 10], "behaviours": ["aggressive", "cowardly", "passive"],
                    "stats": {"health": [25, 50], "attack": [25, 50]}}
        }
    )

    test_player = object_generator.generate("player")
    assert isinstance(test_player, PlayerCharacter)
    assert 90 <= test_player.stats.health <= 110
    assert 90 <= test_player.stats.attack <= 110

    test_obstacle = object_generator.generate("obstacle")
    assert isinstance(test_obstacle, Obstacle)

    test_treasure = object_generator.generate("treasure")
    assert isinstance(test_treasure, Treasure)
    assert test_treasure.name in ["helmet", "boots", "armor"]
    assert -10 <= test_treasure.stats.health <= 30
    assert -10 <= test_treasure.stats.attack <= 30

    test_mob = object_generator.generate("mob")
    assert isinstance(test_mob, Mob)
    assert 1 <= test_mob.level <= 5
    assert 5 <= test_mob.action_radius <= 10
    assert apply_level_multiplier(25, test_mob.level) <= test_mob.stats.health <= apply_level_multiplier(50,
                                                                                                         test_mob.level)
    assert apply_level_multiplier(25, test_mob.level) <= test_mob.stats.attack <= apply_level_multiplier(50,
                                                                                                         test_mob.level)

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
