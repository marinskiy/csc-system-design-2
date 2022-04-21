"""Action manager tests"""

import typing as tp

import pytest

from roguelike.game_engine.env_manager import Map, MapCoordinates, Stats
from roguelike.game_engine.env_manager.map_objects_storage import Treasure, Obstacle, PlayerCharacter
from roguelike.game_engine.game_manager.action_processor.actions import ActionManager
from roguelike.game_engine.game_manager.game_processor.game_state import GameState, Key, Mode, Environment, Inventory


@pytest.fixture(name="state")
def generate_state() -> GameState:
    player = PlayerCharacter(Stats(10.0, 2.0))
    geomap = Map(3, 2)
    geomap.add_object(MapCoordinates(1, 1), player)
    obstacle = Obstacle()
    geomap.add_object(MapCoordinates(0, 1), obstacle)
    treasure = Treasure("Super Helmet", Stats(1.0, 3.0))
    geomap.add_object(MapCoordinates(2, 1), treasure)
    item = Treasure("Trashy boots", Stats(0.0, -2.0))
    inventory = Inventory([item])
    inventory.change_treasure_state(item)
    return GameState(Mode.MAP, Environment(geomap, [player, obstacle, treasure, item]), inventory, player)


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


def test_move_player(state: GameState, actions: ActionManager) -> None:
    geomap = state.environment.map
    player = state.player

    assert geomap.get_coordinates(player) == MapCoordinates(1, 1)

    actions.get_action(Key.S, state)(state)
    assert geomap.get_coordinates(player) == MapCoordinates(1, 1)

    actions.get_action(Key.A, state)(state)
    assert geomap.get_coordinates(player) == MapCoordinates(1, 1)

    actions.get_action(Key.W, state)(state)
    assert geomap.get_coordinates(player) == MapCoordinates(1, 0)

    actions.get_action(Key.D, state)(state)
    assert geomap.get_coordinates(player) == MapCoordinates(2, 0)

    actions.get_action(Key.S, state)(state)
    assert geomap.get_coordinates(player) == MapCoordinates(2, 1)

    actions.get_action(Key.A, state)(state)
    assert geomap.get_coordinates(player) == MapCoordinates(1, 1)


def test_take_treasure(state: GameState, actions: ActionManager) -> None:
    geomap = state.environment.map
    player = state.player
    inventory = state.inventory
    helmet, boots = state.environment.world_objects[2:]

    assert inventory.get_treasures() == (boots, )

    actions.get_action(Key.E, state)(state)
    assert inventory.get_treasures() == (boots,)

    actions.get_action(Key.D, state)(state)

    coordinates = geomap.get_coordinates(player)
    assert coordinates
    assert set(geomap.get_objects(coordinates)) == {player, helmet}
    actions.get_action(Key.E, state)(state)
    assert set(inventory.get_treasures()) == {boots, helmet}
    assert geomap.get_objects(coordinates) == (player, )


def test_inventory_actions(state: GameState, actions: ActionManager) -> None:
    inventory = state.inventory
    helmet, boots = tp.cast(tp.List[Treasure], state.environment.world_objects[2:])

    assert inventory.get_additional_stats() == boots.stats
    actions.get_action(Key.D, state)(state)
    actions.get_action(Key.E, state)(state)
    assert inventory.get_additional_stats() == boots.stats

    actions.get_action(Key.II, state)(state)
    assert inventory.presenter.get_selected() == boots

    actions.get_action(Key.E, state)(state)
    assert inventory.presenter.get_selected() == boots
    assert inventory.get_additional_stats() == Stats(0.0, 0.0)

    actions.get_action(Key.W, state)(state)
    assert inventory.presenter.get_selected() == boots
    actions.get_action(Key.S, state)(state)
    assert inventory.presenter.get_selected() == helmet
    assert inventory.get_additional_stats() == Stats(0.0, 0.0)

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
