"""Action manager tests"""
import random
import typing as tp

import pytest

from roguelike.game_engine.env_manager import Map, MapCoordinates, Stats
from roguelike.game_engine.env_manager.map_objects_storage import Treasure, Obstacle, PlayerCharacter
from roguelike.game_engine.env_manager.enemies import Mob, ConfusedMob, PassiveBehaviour
from roguelike.game_engine.game_manager.action_processor.action_manager import ActionManager
from roguelike.game_engine.game_manager.game_processor.game_state import GameState, Key, Mode, Environment, Inventory


@pytest.fixture(name="helmet")
def generate_helmet() -> Treasure:
    return Treasure("Super Helmet", Stats(1, 3))


@pytest.fixture(name="boots")
def generate_boots() -> Treasure:
    return Treasure("Trashy boots", Stats(0, -2))


@pytest.fixture(name="state")
def generate_state(helmet: Treasure, boots: Treasure) -> GameState:
    player = PlayerCharacter(Stats(10, 2))
    geomap = Map(3, 2)
    geomap.add_object(MapCoordinates(1, 1), player)
    obstacle = Obstacle()
    geomap.add_object(MapCoordinates(0, 1), obstacle)
    geomap.add_object(MapCoordinates(2, 1), helmet)
    inventory = Inventory([boots])
    inventory.change_treasure_state(boots)
    enemy = Mob(3, Stats(7, 1), 3, PassiveBehaviour())
    geomap.add_object(MapCoordinates(0, 0), enemy)
    return GameState(Mode.MAP, Environment(geomap, {enemy}), inventory, player)


@pytest.fixture(name="actions")
def get_actions() -> ActionManager:
    return ActionManager()


def test_switch_mode(state: GameState, actions: ActionManager) -> None:
    assert state.mode == Mode.MAP
    actions.get_action(Key.M, state)(state)
    assert state.mode == Mode.MAP
    actions.get_action(Key.II, state)(state)
    assert state.mode == Mode.INVENTORY
    actions.get_action(Key.II, state)(state)
    assert state.mode == Mode.INVENTORY
    actions.get_action(Key.M, state)(state)
    assert state.mode == Mode.MAP


def test_player_moves_everywhere_on_free_map_and_dont_cross_borders(
        actions: ActionManager,
) -> None:
    player = PlayerCharacter(Stats(1, 1))
    geomap = Map(3, 3)
    geomap.add_object(MapCoordinates(1, 1), player)
    state = GameState(
        Mode.MAP,
        Environment(geomap, set()),
        Inventory([]),
        player,
    )

    assert geomap.get_coordinates(player) == MapCoordinates(1, 1)
    for key, target_coordinates in (
            (Key.W, MapCoordinates(1, 2)),
            (Key.W, MapCoordinates(1, 2)),
            (Key.A, MapCoordinates(0, 2)),
            (Key.A, MapCoordinates(0, 2)),
            (Key.S, MapCoordinates(0, 1)),
            (Key.A, MapCoordinates(0, 1)),
            (Key.S, MapCoordinates(0, 0)),
            (Key.S, MapCoordinates(0, 0)),
            (Key.A, MapCoordinates(0, 0)),
            (Key.D, MapCoordinates(1, 0)),
            (Key.S, MapCoordinates(1, 0)),
            (Key.D, MapCoordinates(2, 0)),
            (Key.S, MapCoordinates(2, 0)),
            (Key.D, MapCoordinates(2, 0)),
            (Key.W, MapCoordinates(2, 1)),
            (Key.D, MapCoordinates(2, 1)),
            (Key.W, MapCoordinates(2, 2)),
            (Key.D, MapCoordinates(2, 2)),
            (Key.W, MapCoordinates(2, 2)),
    ):
        actions.get_action(key, state)(state)
        assert geomap.get_coordinates(player) == target_coordinates


def test_player_does_not_move_through_the_obstacles(
        actions: ActionManager,
) -> None:
    player = PlayerCharacter(Stats(1, 1))
    geomap = Map(3, 3)
    player_initial_coordinates = MapCoordinates(1, 1)
    geomap.add_object(player_initial_coordinates, player)
    geomap.add_object(player_initial_coordinates.left, Obstacle())
    geomap.add_object(player_initial_coordinates.right, Obstacle())
    geomap.add_object(player_initial_coordinates.up, Obstacle())
    geomap.add_object(player_initial_coordinates.down, Obstacle())
    state = GameState(
        Mode.MAP,
        Environment(geomap, set()),
        Inventory([]),
        player,
    )

    assert geomap.get_coordinates(player) == MapCoordinates(1, 1)
    assert geomap.get_coordinates(player) == MapCoordinates(1, 1)
    for key, target_coordinates in (
            (Key.W, MapCoordinates(1, 1)),
            (Key.S, MapCoordinates(1, 1)),
            (Key.A, MapCoordinates(1, 1)),
            (Key.D, MapCoordinates(1, 1)),
    ):
        actions.get_action(key, state)(state)
        assert geomap.get_coordinates(player) == target_coordinates


def test_player_attack(state: GameState, actions: ActionManager) -> None:
    random.seed(2)
    env = state.environment
    geomap = state.environment.map
    player = state.player
    enemy = next(iter(state.environment.enemies))

    assert geomap.get_coordinates(player) == MapCoordinates(1, 1)

    actions.get_action(Key.S, state)(state)
    assert geomap.get_coordinates(player) == MapCoordinates(1, 0)

    actions.get_action(Key.A, state)(state)
    assert geomap.get_coordinates(player) == MapCoordinates(1, 0)
    assert enemy.stats == Stats(3, 1)
    assert not enemy.is_dead()

    actions.get_action(Key.A, state)(state)
    assert geomap.get_coordinates(player) == MapCoordinates(1, 0)
    assert enemy.stats == Stats(1, 1)
    new_enemies = geomap.get_objects(MapCoordinates(0, 0))
    assert len(new_enemies) == 1
    for new_enemy in new_enemies:
        assert isinstance(new_enemy, ConfusedMob)
        for _ in range(2):
            new_enemy.act(env, player)
        assert isinstance(new_enemy, ConfusedMob)
        new_enemy.act(env, player)

    assert (enemy,) == geomap.get_objects(MapCoordinates(0, 0))
    assert not enemy.is_dead()

    actions.get_action(Key.A, state)(state)
    assert geomap.get_coordinates(player) == MapCoordinates(1, 0)
    assert enemy.is_dead()

    actions.get_action(Key.A, state)(state)
    assert geomap.get_coordinates(player) == MapCoordinates(0, 0)


def test_take_treasure(
        state: GameState,
        actions: ActionManager,
        helmet: Treasure,
        boots: Treasure,
) -> None:
    geomap = state.environment.map
    player = state.player
    inventory = state.inventory

    assert inventory.get_treasures() == (boots,)

    actions.get_action(Key.E, state)(state)
    assert inventory.get_treasures() == (boots,)

    actions.get_action(Key.D, state)(state)

    coordinates = geomap.get_coordinates(player)
    assert coordinates
    assert set(geomap.get_objects(coordinates)) == {player, helmet}
    actions.get_action(Key.E, state)(state)
    assert set(inventory.get_treasures()) == {boots, helmet}
    assert geomap.get_objects(coordinates) == (player,)


def test_inventory_actions(
        helmet: Treasure,
        boots: Treasure,
        state: GameState,
        actions: ActionManager,
) -> None:
    inventory = state.inventory

    assert inventory.get_additional_stats() == boots.stats
    actions.get_action(Key.D, state)(state)
    actions.get_action(Key.E, state)(state)
    assert inventory.get_additional_stats() == boots.stats

    actions.get_action(Key.II, state)(state)
    assert inventory.presenter.get_selected() == boots

    actions.get_action(Key.E, state)(state)
    assert inventory.presenter.get_selected() == boots
    assert inventory.get_additional_stats() == Stats(0, 0)

    actions.get_action(Key.W, state)(state)
    assert inventory.presenter.get_selected() == boots
    actions.get_action(Key.S, state)(state)
    assert inventory.presenter.get_selected() == helmet
    assert inventory.get_additional_stats() == Stats(0, 0)

    actions.get_action(Key.E, state)(state)
    assert inventory.presenter.get_selected() == helmet
    assert inventory.get_additional_stats() == helmet.stats

    actions.get_action(Key.W, state)(state)
    actions.get_action(Key.E, state)(state)
    assert inventory.presenter.get_selected() == boots
    assert inventory.get_additional_stats() == boots.stats + helmet.stats


def test_menu_actions(state: GameState, actions: ActionManager) -> None:
    actions.get_action(Key.Q, state)(state)
    assert state.is_running is False


def test_confusion() -> None:
    random.seed(2)
    normal = Mob(1, Stats(2, 2), 1, PassiveBehaviour())
    confused = ConfusedMob(normal, 5, lambda: None)
    geomap = Map(10, 10)
    geomap.add_object(MapCoordinates(5, 5), confused)
    player = PlayerCharacter(Stats(2, 0))
    expected_track = [
        MapCoordinates(4, 5),
        MapCoordinates(3, 5),
        MapCoordinates(2, 5),
        MapCoordinates(3, 5),
        MapCoordinates(3, 4),
    ]
    for coordinate in expected_track:
        confused.act(Environment(geomap, set()), player)
        assert geomap.get_coordinates(confused) == coordinate
