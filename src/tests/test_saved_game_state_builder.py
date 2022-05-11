"""Game loader tests"""

import os

import pytest

from roguelike.game_engine.env_manager import MapCoordinates
from roguelike.game_engine.env_manager.enemies import AggressiveBehaviour, Mob, ReplicatingMob
from roguelike.game_engine.env_manager.map_objects_storage import Stats, Obstacle, Treasure, PlayerCharacter
from roguelike.game_engine.game_manager.game_constructor.saved_game_state_builder import SavedGameStateBuilder
from roguelike.game_engine.game_manager.game_constructor.game_state_director import GameStateDirector


def test_coordinates_load_correctly() -> None:
    assert SavedGameStateBuilder._load_coordinates([0, 1]) == MapCoordinates(0, 1)  # pylint: disable=W0212

    with pytest.raises(ValueError):
        SavedGameStateBuilder._load_coordinates([])  # pylint: disable=W0212
    with pytest.raises(ValueError):
        SavedGameStateBuilder._load_coordinates([0])  # pylint: disable=W0212
    with pytest.raises(ValueError):
        SavedGameStateBuilder._load_coordinates([0, 1, 2])  # pylint: disable=W0212


def test_stats_load_correctly() -> None:
    assert SavedGameStateBuilder._load_stats(  # pylint: disable=W0212
        {"health": 100, "attack": 100}) == Stats(health=100, attack=100)

    with pytest.raises(ValueError):
        SavedGameStateBuilder._load_stats({})  # pylint: disable=W0212
    with pytest.raises(ValueError):
        SavedGameStateBuilder._load_stats({"health": 100, "attack": 100, "defence": 100})  # pylint: disable=W0212


def test_obstacle_load_correctly() -> None:
    assert isinstance(SavedGameStateBuilder._load_obstacle({}), Obstacle)  # pylint: disable=W0212

    with pytest.raises(ValueError):
        SavedGameStateBuilder._load_obstacle({"health": 100, "attack": 100, "defence": 100})  # pylint: disable=W0212


def test_treasure_load_correctly() -> None:
    test_treasure = SavedGameStateBuilder._load_treasure(  # pylint: disable=W0212
        {"name": "Super Helmet", "stats": {"health": 10, "attack": 0}})
    assert test_treasure.name == "Super Helmet"
    assert test_treasure.stats == Stats(10, 0)

    with pytest.raises(ValueError):
        SavedGameStateBuilder._load_treasure({})  # pylint: disable=W0212
    with pytest.raises(ValueError):
        SavedGameStateBuilder._load_treasure({"health": 100, "attack": 100, "defence": 100})  # pylint: disable=W0212


def test_mob_load_correctly() -> None:
    test_mob = SavedGameStateBuilder._load_mob(  # pylint: disable=W0212
        {
            "style": "normal",
            "level": 1,
            "radius": 7,
            "behaviour": "aggressive",
            "stats": {"health": 30, "attack": 10}

        }
    )
    assert test_mob.level == 1
    assert test_mob.action_radius == 7
    assert isinstance(test_mob._behaviour, AggressiveBehaviour)  # pylint: disable=W0212
    assert test_mob.stats == Stats(30, 10)

    with pytest.raises(ValueError):
        SavedGameStateBuilder._load_mob({})  # pylint: disable=W0212
    with pytest.raises(ValueError):
        SavedGameStateBuilder._load_mob(  # pylint: disable=W0212
            {
                "level": 1,
                "behaviour": "aggressive",
                "stats": {"health": 30, "attack": 10}
            }
        )


def test_replicating_mob_load_correctly() -> None:
    test_replicating_mob = SavedGameStateBuilder._load_replicating_mob(  # pylint: disable=W0212
        {
            "level": 1,
            "radius": 7,
            "behaviour": "aggressive",
            "stats": {"health": 30, "attack": 10},
            "replication_rate": 0.5,
            "replication_rate_decay": 0.5
        }
    )

    assert test_replicating_mob.level == 1
    assert test_replicating_mob.action_radius == 7
    assert isinstance(test_replicating_mob._behaviour, AggressiveBehaviour)  # pylint: disable=W0212
    assert test_replicating_mob.stats == Stats(30, 10)
    assert test_replicating_mob._replication_rate == 0.5  # pylint: disable=W0212
    assert test_replicating_mob._replication_rate_decay == 0.5  # pylint: disable=W0212

    with pytest.raises(ValueError):
        SavedGameStateBuilder._load_replicating_mob({})  # pylint: disable=W0212
    with pytest.raises(ValueError):
        SavedGameStateBuilder._load_replicating_mob(  # pylint: disable=W0212
            {
                "level": 1,
                "behaviour": "aggressive",
                "stats": {"health": 30, "attack": 10}
            }
        )


def test_player_load_correctly() -> None:
    test_player = SavedGameStateBuilder._load_player({"stats": {"health": 10, "attack": 0}})  # pylint: disable=W0212
    assert test_player.stats == Stats(10, 0)

    with pytest.raises(ValueError):
        SavedGameStateBuilder._load_player({})  # pylint: disable=W0212
    with pytest.raises(ValueError):
        SavedGameStateBuilder._load_player(  # pylint: disable=W0212
            {"name": "Super Helmet", "stats": {"health": 10, "attack": 0}})


def test_map_object_load_correctly() -> None:
    test_object, coords = SavedGameStateBuilder._load_world_object(  # pylint: disable=W0212
        {"type": "player", "pos": [10, 10], "settings": {"stats": {"health": 100, "attack": 100}}})
    assert isinstance(test_object, PlayerCharacter)
    assert coords == MapCoordinates(10, 10)

    test_object, coords = SavedGameStateBuilder._load_world_object(  # pylint: disable=W0212
        {"type": "obstacle", "pos": [0, 0], "settings": {}})
    assert isinstance(test_object, Obstacle)
    assert coords == MapCoordinates(0, 0)

    test_object, coords = SavedGameStateBuilder._load_world_object(  # pylint: disable=W0212
        {"type": "treasure", "pos": [20, 20],
         "settings": {"name": "Super Helmet", "stats": {"health": 10, "attack": 0}}})
    assert isinstance(test_object, Treasure)
    assert coords == MapCoordinates(20, 20)

    test_object, coords = SavedGameStateBuilder._load_world_object(  # pylint: disable=W0212
        {"type": "mob", "pos": [37, 35],
         "settings": {"style": 0, "level": 1, "radius": 7, "behaviour": "aggressive",
                      "stats": {"health": 30, "attack": 10}}})
    assert isinstance(test_object, Mob)
    assert coords == MapCoordinates(37, 35)


def test_map_load_correctly() -> None:
    test_map = SavedGameStateBuilder._load_map({"width": 60, "height": 40})  # pylint: disable=W0212+

    assert test_map._width == 60  # pylint: disable=W0212+
    assert test_map._height == 40  # pylint: disable=W0212+

    with pytest.raises(ValueError):
        SavedGameStateBuilder._load_map({})  # pylint: disable=W0212


def test_load_from_file() -> None:
    file_path = os.path.join(os.path.dirname(__file__), "test_game.json")
    builder = SavedGameStateBuilder()
    builder.set_path(file_path)

    state = GameStateDirector(builder).construct()

    assert state.player.stats == Stats(100, 100)

    assert isinstance(list(state.environment.map.get_objects(MapCoordinates(0, 0)))[0],
                      Obstacle)
    assert isinstance(list(state.environment.map.get_objects(MapCoordinates(7, 7)))[0],
                      Obstacle)
    assert isinstance(list(state.environment.map.get_objects(MapCoordinates(20, 20)))[0],
                      Treasure)
    assert isinstance(list(state.environment.map.get_objects(MapCoordinates(0, 20)))[0],
                      Treasure)
    assert isinstance(list(state.environment.map.get_objects(MapCoordinates(10, 10)))[0],
                      PlayerCharacter)
    assert isinstance(list(state.environment.map.get_objects(MapCoordinates(37, 35)))[0],
                      Mob)
    assert isinstance(list(state.environment.map.get_objects(MapCoordinates(5, 5)))[0],
                      ReplicatingMob)

    assert len(state.environment.enemies) == 2
