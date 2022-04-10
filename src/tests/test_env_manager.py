"""Env manager tests"""

import pytest

from roguelike.game_engine.env_manager.map import Map, MapCoordinates
from roguelike.game_engine.env_manager.map_objects_storage import (
    Stats, PlayerCharacter, Obstacle, Treasure,
)


def test_stats_sums_correctly() -> None:
    assert Stats(1, 2) != Stats(2, 3)
    assert Stats(1, 2) == Stats(1, 2)
    assert Stats(0, 0) + Stats(1, 1) == Stats(1, 1)
    assert Stats(1, 1) + Stats(1, 1) == Stats(2, 2)
    assert Stats(1, 2) + Stats(1, 1) == Stats(2, 3)
    with pytest.raises(NotImplementedError):
        Stats(0, 0) + 2  # pylint: disable=expression-not-assigned


def test_treasure_creates_properly() -> None:
    treasure_name = 'power stick'
    treasure = Treasure(treasure_name, Stats(0, 1))
    assert treasure.name == treasure_name
    assert treasure.stats == Stats(0, 1)


def test_player_character_creates_properly() -> None:
    player_character = PlayerCharacter(Stats(1, 1))
    assert player_character.stats == Stats(1, 1)


def test_map_creates_correctly() -> None:
    with pytest.raises(ValueError):
        Map(0, 0)
    with pytest.raises(ValueError):
        Map(0, 1)
    with pytest.raises(ValueError):
        Map(1, 0)
    Map(3, 3)


def test_map_handles_map_objects_operations() -> None:
    map_ = Map(3, 3)
    obstacle = Obstacle()
    object_coordinates = MapCoordinates(0, 0)
    map_.add_object(object_coordinates, obstacle)
    returned_objects = map_.get_objects(object_coordinates)
    assert len(returned_objects) == 1
    assert obstacle in returned_objects

    updated_object_coordinates = MapCoordinates(1, 2)
    # todo: test moving to wrong coordinates
    map_.move_to(obstacle, updated_object_coordinates)
    assert not map_.get_objects(object_coordinates)
    assert obstacle in map_.get_objects(updated_object_coordinates)

    map_.remove_object(obstacle)
    assert not map_.get_objects(updated_object_coordinates)

    # todo: test on several objects


def test_inventory_lists_objects_properly() -> None:
    # todo
    pass


def test_game_state_creates_properly() -> None:
    # todo
    pass


def test_environment_creates_properly() -> None:
    # todo
    pass
