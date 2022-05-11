"""Game loop tests"""

import os

import pytest

from roguelike.game_engine.env_manager import MapCoordinates
from roguelike.game_engine.env_manager.map_objects_storage import PlayerCharacter
from roguelike.game_engine.game_manager.game_constructor.saved_game_state_builder import SavedGameStateBuilder
from roguelike.game_engine.game_manager.game_constructor.game_state_director import GameStateDirector
from roguelike.game_engine.game_manager.game_processor.game_loop import GameLoop
from roguelike.game_engine.game_manager.game_processor.game_state import Key, Mode


@pytest.fixture(name="loop")
def generate_game_loop() -> GameLoop:
    file_path = os.path.join(os.path.dirname(__file__), "test_game.json")
    state = GameStateDirector(SavedGameStateBuilder().set_path(file_path)).construct()
    return GameLoop(state)


def test_player_makes_move(loop: GameLoop) -> None:
    new_state = loop.run_game_turn(Key.S)
    assert isinstance(list(new_state.environment.map.get_objects(MapCoordinates(10, 9)))[0],
                      PlayerCharacter)
    assert len(list(new_state.environment.map.get_objects(MapCoordinates(10, 10)))) == 0

    new_state = loop.run_game_turn(Key.A)
    assert isinstance(list(new_state.environment.map.get_objects(MapCoordinates(9, 9)))[0],
                      PlayerCharacter)
    assert len(list(new_state.environment.map.get_objects(MapCoordinates(10, 9)))) == 0

    new_state = loop.run_game_turn(Key.W)
    assert isinstance(list(new_state.environment.map.get_objects(MapCoordinates(9, 10)))[0],
                      PlayerCharacter)
    assert len(list(new_state.environment.map.get_objects(MapCoordinates(9, 9)))) == 0

    new_state = loop.run_game_turn(Key.D)
    assert isinstance(list(new_state.environment.map.get_objects(MapCoordinates(10, 10)))[0],
                      PlayerCharacter)
    assert len(list(new_state.environment.map.get_objects(MapCoordinates(9, 10)))) == 0


def test_changes_mode(loop: GameLoop) -> None:
    new_state = loop.run_game_turn(Key.II)
    assert new_state.mode == Mode.INVENTORY

    new_state = loop.run_game_turn(Key.II)
    assert new_state.mode == Mode.INVENTORY

    new_state = loop.run_game_turn(Key.M)
    assert new_state.mode == Mode.MAP

    new_state = loop.run_game_turn(Key.M)
    assert new_state.mode == Mode.MAP


def test_quits(loop: GameLoop) -> None:
    new_state = loop.run_game_turn(Key.Q)
    assert not new_state.is_running
