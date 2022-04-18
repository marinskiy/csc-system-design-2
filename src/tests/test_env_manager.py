"""Env manager tests"""
# pylint: disable=redefined-outer-name

import typing as tp

import pytest

from roguelike.game_engine.env_manager.env_manager import Inventory, Environment
from roguelike.game_engine.env_manager.map import Map, MapCoordinates
from roguelike.game_engine.env_manager.map_objects_storage import (
    Stats, PlayerCharacter, Obstacle, Treasure,
)
from roguelike.game_engine.game_manager.game_processor.game_state import GameState, Mode


@pytest.fixture()
def treasures() -> tp.Collection[Treasure]:
    return (
        Treasure('power stick', Stats(0, 1)),
        Treasure('speed boots', Stats(1, 0)),
        Treasure('general stats booster', Stats(1, 1)),
    )


@pytest.fixture()
def obstacle_coordinates() -> MapCoordinates:
    return MapCoordinates(0, 0)


@pytest.fixture()
def obstacle() -> Obstacle:
    return Obstacle()


@pytest.fixture()
def map_with_obstacle(
        obstacle_coordinates: MapCoordinates,
        obstacle: Obstacle,
) -> Map:
    map_ = Map(3, 3)
    map_.add_object(obstacle_coordinates, obstacle)
    return map_


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


def test_map_creates_correctly() -> None:
    with pytest.raises(ValueError):
        Map(0, 0)
    with pytest.raises(ValueError):
        Map(0, 1)
    with pytest.raises(ValueError):
        Map(1, 0)
    Map(3, 3)


def test_map_lists_objects(
        map_with_obstacle: Map,
        obstacle_coordinates: MapCoordinates,
        obstacle: Obstacle,
) -> None:
    returned_objects = map_with_obstacle.get_objects(obstacle_coordinates)
    assert len(returned_objects) == 1
    assert obstacle in returned_objects


def test_map_moves_objects(
        map_with_obstacle: Map,
        obstacle_coordinates: MapCoordinates,
        obstacle: Obstacle,
) -> None:
    updated_object_coordinates = MapCoordinates(1, 2)
    map_with_obstacle.move_to(obstacle, updated_object_coordinates)
    assert not map_with_obstacle.get_objects(obstacle_coordinates)
    assert obstacle in map_with_obstacle.get_objects(updated_object_coordinates)

    with pytest.raises(ValueError):
        map_with_obstacle.move_to(obstacle, MapCoordinates(3, 0))
        map_with_obstacle.move_to(obstacle, MapCoordinates(0, 3))
        map_with_obstacle.move_to(obstacle, MapCoordinates(3, 3))
        map_with_obstacle.move_to(obstacle, MapCoordinates(-1, 0))
        map_with_obstacle.move_to(obstacle, MapCoordinates(0, -1))
        map_with_obstacle.move_to(obstacle, MapCoordinates(-1, -1))


def test_get_coordinates() -> None:
    map_ = Map(2, 2)
    obstacle_0 = Obstacle()
    obstacle_1 = Obstacle()
    obstacle_2 = Obstacle()
    obstacle_3 = Obstacle()
    map_.add_object(MapCoordinates(0, 0), obstacle_0)
    map_.add_object(MapCoordinates(0, 1), obstacle_1)
    map_.add_object(MapCoordinates(1, 0), obstacle_2)
    map_.add_object(MapCoordinates(1, 1), obstacle_3)

    assert map_.get_coordinates(obstacle_0) == MapCoordinates(0, 0)
    assert map_.get_coordinates(obstacle_1) == MapCoordinates(0, 1)
    assert map_.get_coordinates(obstacle_2) == MapCoordinates(1, 0)
    assert map_.get_coordinates(obstacle_3) == MapCoordinates(1, 1)


def test_map_removes_objects(
        map_with_obstacle: Map,
        obstacle_coordinates: MapCoordinates,
        obstacle: Obstacle,
) -> None:
    map_with_obstacle.remove_object(obstacle)
    assert not map_with_obstacle.get_objects(obstacle_coordinates)


def test_map_removes_objects_after_they_been_moved(
        map_with_obstacle: Map,
        obstacle_coordinates: MapCoordinates,
        obstacle: Obstacle,
) -> None:
    updated_object_coordinates = MapCoordinates(1, 2)
    map_with_obstacle.move_to(obstacle, updated_object_coordinates)
    assert not map_with_obstacle.get_objects(obstacle_coordinates)
    assert obstacle in map_with_obstacle.get_objects(updated_object_coordinates)

    map_with_obstacle.remove_object(obstacle)
    assert not map_with_obstacle.get_objects(updated_object_coordinates)


def test_inventory_lists_all_objects(
        treasures: tp.Collection[Treasure],
) -> None:
    inventory = Inventory(treasures)
    treasures_listing = inventory.get_treasures()
    for treasure in treasures:
        assert treasure in treasures_listing


def test_inventory_calculates_additional_stats_correctly(
        treasures: tp.Collection[Treasure],
) -> None:
    # no treasures in inventory
    inventory = Inventory([])
    assert inventory.get_additional_stats() == Stats(0, 0)

    # 3 treasures in inventory, 0 is on
    inventory = Inventory(treasures)
    for treasure in treasures:
        inventory.put_on(treasure)
        assert inventory.get_additional_stats() == treasure.stats
        inventory.put_off(treasure)

    total_stats = Stats(0, 0)
    inventory = Inventory(treasures)
    for treasure in treasures:
        inventory.put_on(treasure)
        total_stats += treasure.stats
    additional_stats = inventory.get_additional_stats()
    assert additional_stats == total_stats


def test_environment_creates_properly() -> None:
    Environment(map=Map(1, 1), world_objects=[])


def test_player_character_creates_properly() -> None:
    player_character = PlayerCharacter(Stats(1, 1))
    assert player_character.stats == Stats(1, 1)


def test_game_state_creates_properly() -> None:
    GameState(
        mode=Mode.MAP,
        environment=Environment(Map(1, 1), []),
        inventory=Inventory([]),
        player=PlayerCharacter(Stats(1, 0)),
    )
