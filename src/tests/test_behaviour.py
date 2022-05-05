"""Mob behaviour tests"""
# pylint: disable=redefined-outer-name
import typing as tp
import pytest

from roguelike.game_engine.env_manager import MapCoordinates, Map, Environment
from roguelike.game_engine.env_manager.enemies import Mob, AggressiveBehaviour, PassiveBehaviour, CowardlyBehaviour
from roguelike.game_engine.env_manager.map_objects_storage import Obstacle, PlayerCharacter, Stats


@pytest.fixture()
def obstacle_coordinates() -> MapCoordinates:
    return MapCoordinates(2, 1)


@pytest.fixture()
def player_coordinates() -> MapCoordinates:
    return MapCoordinates(0, 0)


@pytest.fixture()
def obstacle() -> Obstacle:
    return Obstacle()


@pytest.fixture()
def player() -> PlayerCharacter:
    return PlayerCharacter(Stats(100, 100))


@pytest.fixture()
def map_with_obstacle_and_player(
        obstacle_coordinates: MapCoordinates,
        obstacle: Obstacle,
        player_coordinates: MapCoordinates,
        player: PlayerCharacter
) -> tp.Tuple[Environment, PlayerCharacter]:
    env = Environment(map=Map(3, 4), enemies=set())
    env.map.add_object(obstacle_coordinates, obstacle)
    env.map.add_object(player_coordinates, player)
    return env, player


@pytest.fixture()
def aggressive_mob() -> Mob:
    return Mob(1, Stats(10, 10), 2, AggressiveBehaviour())


@pytest.fixture()
def passive_mob() -> Mob:
    return Mob(1, Stats(10, 10), 2, PassiveBehaviour())


@pytest.fixture()
def cowardly_mob() -> Mob:
    return Mob(1, Stats(10, 10), 2, CowardlyBehaviour())


def test_aggressive_behaviour_within_action_radius(
        map_with_obstacle_and_player: tp.Tuple[Environment, PlayerCharacter],
        aggressive_mob: Mob,
) -> None:
    env, player = map_with_obstacle_and_player
    geomap = env.map
    geomap.add_object(MapCoordinates(1, 1), aggressive_mob)

    aggressive_mob.act(env, player)

    first_step_mob_coordinates = geomap.get_coordinates(aggressive_mob)
    assert first_step_mob_coordinates in [MapCoordinates(1, 0), MapCoordinates(0, 1)]
    assert player.stats.health == 100

    aggressive_mob.act(env, player)

    second_step_mob_coordinates = geomap.get_coordinates(aggressive_mob)
    assert first_step_mob_coordinates == second_step_mob_coordinates
    assert player.stats.health == 90


def check_mob_actions_out_of_action_radius(
        mob: Mob,
        env: Environment,
        player: PlayerCharacter,
) -> None:
    env.map.add_object(MapCoordinates(1, 2), mob)
    mob.act(env, player)

    assert env.map.get_coordinates(mob) == MapCoordinates(1, 2)
    assert player.stats.health == 100
    env.map.remove_object(mob)


def test_behaviour_out_of_action_radius(
        map_with_obstacle_and_player: tp.Tuple[Environment, PlayerCharacter],
        aggressive_mob: Mob,
        passive_mob: Mob,
        cowardly_mob: Mob,
) -> None:
    env, player = map_with_obstacle_and_player
    for mob in [aggressive_mob, passive_mob, cowardly_mob]:
        check_mob_actions_out_of_action_radius(mob, env, player)


def test_passive_behaviour_within_action_radius(
        map_with_obstacle_and_player: tp.Tuple[Environment, PlayerCharacter],
        passive_mob: Mob,
) -> None:
    env, player = map_with_obstacle_and_player
    env.map.add_object(MapCoordinates(1, 1), passive_mob)

    passive_mob.act(env, player)

    assert env.map.get_coordinates(passive_mob) == MapCoordinates(1, 1)
    assert player.stats.health == 100


def test_cowardly_behaviour_within_action_radius(
        map_with_obstacle_and_player: tp.Tuple[Environment, PlayerCharacter],
        cowardly_mob: Mob,
) -> None:
    env, player = map_with_obstacle_and_player
    env.map.add_object(MapCoordinates(1, 1), cowardly_mob)

    cowardly_mob.act(env, player)

    assert env.map.get_coordinates(cowardly_mob) == MapCoordinates(1, 2)
    assert player.stats.health == 100
