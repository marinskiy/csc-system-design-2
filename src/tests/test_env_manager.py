"""Env manager tests"""
# pylint: disable=redefined-outer-name
import random
import typing as tp

import pytest

from roguelike.game_engine.env_manager import Inventory, Environment, Map, MapCoordinates
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


def test_coordinates_neighbours(map_with_obstacle: Map) -> None:
    coordinates = MapCoordinates(0, 0)
    assert coordinates.up == MapCoordinates(0, 1)
    assert coordinates.down == MapCoordinates(0, -1)
    assert coordinates.left == MapCoordinates(-1, 0)
    assert coordinates.right == MapCoordinates(1, 0)

    coordinates = MapCoordinates(0, 0)
    proposed_neighbours = map_with_obstacle.get_neighbours(coordinates)
    assert len(proposed_neighbours) == 2
    assert coordinates.up in proposed_neighbours
    assert coordinates.right in proposed_neighbours

    coordinates = MapCoordinates(1, 0)
    proposed_neighbours = map_with_obstacle.get_neighbours(coordinates)
    assert len(proposed_neighbours) == 3
    assert coordinates.up in proposed_neighbours
    assert coordinates.left in proposed_neighbours
    assert coordinates.right in proposed_neighbours

    coordinates = MapCoordinates(0, 1)
    proposed_neighbours = map_with_obstacle.get_neighbours(coordinates)
    assert len(proposed_neighbours) == 3
    assert coordinates.up in proposed_neighbours
    assert coordinates.down in proposed_neighbours
    assert coordinates.right in proposed_neighbours

    coordinates = MapCoordinates(2, 2)
    proposed_neighbours = map_with_obstacle.get_neighbours(coordinates)
    assert len(proposed_neighbours) == 2
    assert coordinates.down in proposed_neighbours
    assert coordinates.left in proposed_neighbours

    coordinates = MapCoordinates(1, 2)
    proposed_neighbours = map_with_obstacle.get_neighbours(coordinates)
    assert len(proposed_neighbours) == 3
    assert coordinates.down in proposed_neighbours
    assert coordinates.left in proposed_neighbours
    assert coordinates.right in proposed_neighbours

    coordinates = MapCoordinates(2, 1)
    proposed_neighbours = map_with_obstacle.get_neighbours(coordinates)
    assert len(proposed_neighbours) == 3
    assert coordinates.up in proposed_neighbours
    assert coordinates.down in proposed_neighbours
    assert coordinates.left in proposed_neighbours

    coordinates = MapCoordinates(1, 1)
    proposed_neighbours = map_with_obstacle.get_neighbours(coordinates)
    assert len(proposed_neighbours) == 4
    assert coordinates.up in proposed_neighbours
    assert coordinates.down in proposed_neighbours
    assert coordinates.left in proposed_neighbours
    assert coordinates.right in proposed_neighbours


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


def test_map_does_not_move_objects_to_out_of_map_coordinates(
        map_with_obstacle: Map,
        obstacle_coordinates: MapCoordinates,
        obstacle: Obstacle,
) -> None:
    for new_coordinates in (
            MapCoordinates(3, 0),
            MapCoordinates(0, 3),
            MapCoordinates(3, 3),
            MapCoordinates(-1, 0),
            MapCoordinates(0, -1),
            MapCoordinates(-1, -1),
    ):
        map_with_obstacle.move_to(obstacle, new_coordinates)
        assert obstacle_coordinates == map_with_obstacle.get_coordinates(obstacle)


def test_map_returns_coordinates() -> None:
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


def test_map_does_not_return_out_of_map_coordinates(
        obstacle: Obstacle,
) -> None:
    map_ = Map(1, 1)
    map_.add_object(MapCoordinates(0, 0), obstacle)
    for coordinates in (
            MapCoordinates(0, -1),
            MapCoordinates(-1, 0),
            MapCoordinates(-1, -1),
            MapCoordinates(0, 1),
            MapCoordinates(1, 0),
            MapCoordinates(1, 1),
    ):
        assert map_.get_objects(coordinates) == ()


def test_map_does_not_add_objects_to_out_of_map_coordinates() -> None:
    map_ = Map(1, 1)
    for coordinates in (
            MapCoordinates(0, -1),
            MapCoordinates(-1, 0),
            MapCoordinates(-1, -1),
            MapCoordinates(0, 1),
            MapCoordinates(1, 0),
            MapCoordinates(1, 1),
    ):
        obstacle = Obstacle()
        map_.add_object(coordinates, obstacle)
        assert map_.get_coordinates(obstacle) is None


def test_map_removes_objects(
        map_with_obstacle: Map,
        obstacle_coordinates: MapCoordinates,
        obstacle: Obstacle,
) -> None:
    map_with_obstacle.remove_object(obstacle)
    assert not map_with_obstacle.get_objects(obstacle_coordinates)


def test_map_does_not_add_object_that_is_already_on_the_map(
        map_with_obstacle: Map,
        obstacle: Obstacle,
        obstacle_coordinates: MapCoordinates,
) -> None:
    new_coordinates = MapCoordinates(obstacle_coordinates.x + 1,
                                     obstacle_coordinates.y)
    with pytest.raises(ValueError):
        map_with_obstacle.add_object(new_coordinates, obstacle)


def test_map_does_not_move_object_that_is_not_on_the_map(
        obstacle: Obstacle,
) -> None:
    map_ = Map(1, 1)
    map_.move_to(obstacle, MapCoordinates(0, 0))
    assert map_.get_objects(MapCoordinates(0, 0)) == ()


def test_map_does_not_remove_object_that_is_not_on_the_map() -> None:
    map_ = Map(1, 1)
    obstacle_first = Obstacle()
    obstacle_second = Obstacle()
    map_.add_object(MapCoordinates(0, 0), obstacle_first)
    map_.remove_object(obstacle_second)
    objects_listing = map_.get_objects(MapCoordinates(0, 0))
    assert len(objects_listing) == 1
    assert obstacle_first in objects_listing


def test_map_does_not_get_object_that_is_not_on_the_map(
        obstacle: Obstacle,
) -> None:
    map_ = Map(1, 1)
    assert map_.get_coordinates(obstacle) is None


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
        inventory.change_treasure_state(treasure)
        assert inventory.get_additional_stats() == treasure.stats
        inventory.change_treasure_state(treasure)

    total_stats = Stats(0, 0)
    inventory = Inventory(treasures)
    for treasure in treasures:
        inventory.change_treasure_state(treasure)
        total_stats += treasure.stats
    additional_stats = inventory.get_additional_stats()
    assert additional_stats == total_stats


def test_environment_creates_properly() -> None:
    Environment(map=Map(1, 1), enemies=set())


def test_player_character_creates_properly() -> None:
    player_character = PlayerCharacter(Stats(1, 1))
    assert player_character.stats == Stats(1, 1)


def test_game_state_creates_properly() -> None:
    GameState(
        mode=Mode.MAP,
        environment=Environment(Map(1, 1), set()),
        inventory=Inventory([]),
        player=PlayerCharacter(Stats(1, 0)),
    )


def test_player_character_levels_up() -> None:
    random.seed(42)
    player_character = PlayerCharacter(Stats(1, 1))

    # test neg exp protection
    with pytest.raises(ValueError):
        player_character.gain_experience(-1)

    # test lvl up
    assert player_character.level == 1
    exp_needed = player_character._calculate_exp_needed_for_new_level()  # pylint: disable=protected-access
    player_character.gain_experience(exp_needed)
    assert player_character.level == 2
    assert player_character._experience == 0  # pylint: disable=protected-access
    assert player_character.stats == Stats(2, 2)

    # test incremental exp gaining
    exp_needed = player_character._calculate_exp_needed_for_new_level()  # pylint: disable=protected-access
    player_character.gain_experience(exp_needed - 1)
    assert player_character.level == 2
    player_character.gain_experience(1)
    assert player_character.level == 3
    assert player_character._experience == 0  # pylint: disable=protected-access
    assert player_character.stats == Stats(2, 3)

    # test rest of exp transitions properly
    exp_needed = player_character._calculate_exp_needed_for_new_level()  # pylint: disable=protected-access
    player_character.gain_experience(exp_needed + 1)
    assert player_character.level == 4
    assert player_character._experience == 1  # pylint: disable=protected-access
    assert player_character.stats == Stats(2, 4)

    player_character._level_up()  # pylint: disable=protected-access
    assert player_character.stats == Stats(3, 5)


@pytest.mark.parametrize(
    ['coord_first', 'coord_second'],
    [
        [MapCoordinates(0, 0), MapCoordinates(1, 0)],
        [MapCoordinates(0, 0), MapCoordinates(0, 1)],
        [MapCoordinates(0, 0), MapCoordinates(1, 1)],
        [MapCoordinates(1, 0), MapCoordinates(0, 1)],
    ]
)
def test_coordinates_are_compared_correctly(
        coord_first: MapCoordinates,
        coord_second: MapCoordinates,
) -> None:
    assert coord_first < coord_second


def test_map_calculates_distance_properly(
) -> None:
    map_ = Map(10, 10)
    obstacle_first = Obstacle()
    obstacle_second = Obstacle()
    map_.add_object(MapCoordinates(0, 0), obstacle_first)
    map_.add_object(MapCoordinates(9, 9), obstacle_second)
    assert map_.get_distance_between_objects(obstacle_first, obstacle_second) == 18

    map_.move_to(obstacle_second, MapCoordinates(0, 0))
    assert map_.get_distance_between_objects(obstacle_first, obstacle_second) == 0

    map_.move_to(obstacle_second, MapCoordinates(0, 1))
    assert map_.get_distance_between_objects(obstacle_first, obstacle_second) == 1

    map_.move_to(obstacle_second, MapCoordinates(1, 1))
    assert map_.get_distance_between_objects(obstacle_first, obstacle_second) == 2

    map_.move_to(obstacle_second, MapCoordinates(1, 2))
    assert map_.get_distance_between_objects(obstacle_first, obstacle_second) == 3

    map_.move_to(obstacle_second, MapCoordinates(1, 2))
    assert map_.get_distance_between_objects(obstacle_first, obstacle_second) == \
           map_.get_distance_between_objects(obstacle_second, obstacle_first)
