"""Tests for all mobs kinds"""

import random
import typing as tp

from roguelike.game_engine.env_manager import MapCoordinates, Map, Environment
from roguelike.game_engine.env_manager.enemies import ReplicatingMob, PassiveBehaviour, NPC
from roguelike.game_engine.env_manager.map_objects_storage import Obstacle, Stats, PlayerCharacter


def count_total_class_instances_on_map(geomap: Map, searched_class: tp.Type[NPC]) -> int:
    return sum(
        isinstance(obj, searched_class)
        for objs in geomap._coord_to_cell.values()  # pylint: disable=protected-access
        for obj in objs.items
    )


def check_mob_is_the_same(mob_first: NPC, mob_second: NPC) -> None:
    mob_first_info = (
        mob_first.level,
        mob_first.stats,
        mob_first.action_radius,
        mob_first.attack_power,
    )
    mob_second_info = (
        mob_second.level,
        mob_second.stats,
        mob_second.action_radius,
        mob_second.attack_power,
    )
    assert mob_first_info == mob_second_info


def test_replicating_mob_replicates() -> None:
    random.seed(0)

    obstacle_coordinates = MapCoordinates(0, 0)
    obstacle = Obstacle()
    env = Environment(Map(4, 4), set())
    env.map.add_object(obstacle_coordinates, obstacle)
    mob = ReplicatingMob(
        level=1, stats=Stats(0, 0),
        radius=1, behaviour=PassiveBehaviour(),
        replication_probability=1.0,
    )
    env.enemies.add(mob)
    mob_coordinates = MapCoordinates(1, 1)
    env.map.add_object(mob_coordinates, mob)
    player_coordinates = MapCoordinates(3, 3)
    player = PlayerCharacter(Stats(1, 1))
    env.map.add_object(player_coordinates, player)
    # |...P|
    # |....|
    # |.M..|
    # |O...|
    assert env.enemies == {mob, }
    assert count_total_class_instances_on_map(env.map, ReplicatingMob) == 1
    mob.act(env, player)
    assert count_total_class_instances_on_map(env.map, ReplicatingMob) == 2
    # |...P|
    # |....|
    # |.M..|
    # |OM..|
    # env.map._coord_to_cell
    objects_at_coord = list(env.map.get_objects(MapCoordinates(1, 2)))
    assert len(objects_at_coord) == 1
    first_replica = objects_at_coord[0]
    assert isinstance(first_replica, ReplicatingMob)
    assert env.enemies == {mob, first_replica}
    check_mob_is_the_same(mob, first_replica)
    # |...P|
    # |.M..|
    # |.M..|
    # |O...|
    mob.act(env, player)
    assert count_total_class_instances_on_map(env.map, ReplicatingMob) == 3
    # |...P|
    # |.M..|
    # |.M..|
    # |OM..|
    objects_at_coord = list(env.map.get_objects(MapCoordinates(1, 0)))
    assert len(objects_at_coord) == 1
    second_replica = objects_at_coord[0]
    assert isinstance(second_replica, ReplicatingMob)
    assert env.enemies == {mob, first_replica, second_replica}
    check_mob_is_the_same(mob, second_replica)


def test_replicating_mob_does_not_replicate_into_occupied_cells() -> None:
    # todo
    pass


def test_replicating_mob_acts_after_replication() -> None:
    # todo
    pass


def test_replicated_mob_is_independent_of_parent() -> None:
    # todo
    pass


def test_replication_works_with_decreasing_probability() -> None:
    # todo
    pass
