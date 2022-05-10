"""
Contains game main loop
"""

import argparse
import os
import typing as tp

from roguelike.game_engine.game_manager import GameLoop
from roguelike.game_engine.game_manager.game_constructor.random_game_state_builder import RandomGameStateBuilder
from roguelike.game_engine.game_manager.game_constructor.saved_game_state_builder import SavedGameStateBuilder
from roguelike.game_engine.game_manager.game_constructor.game_state_director import GameStateDirector, GameStateBuilder
from roguelike.game_engine.game_manager.game_processor.game_state import GameState
from roguelike.ui.drawer import Drawer
from roguelike.ui.keyboard_interpreter import KeyboardInterpreter


def parse_arguments() -> tp.Any:
    parser = argparse.ArgumentParser(description="Game command line arguments.")
    parser.add_argument("-path", type=map_path, help="path to the map")
    return parser.parse_args()


def map_path(path: str) -> str:
    if os.path.isfile(path) and path.endswith(".json"):
        return path
    else:
        raise argparse.ArgumentTypeError(f"map path {path} is not a valid path")


def get_game_state() -> GameState:
    args = parse_arguments()
    builder: GameStateBuilder

    if args.path is not None:
        builder = SavedGameStateBuilder().set_path(args.path)
    else:
        builder = RandomGameStateBuilder()

    return GameStateDirector(builder).construct()


if __name__ == "__main__":
    current_state = get_game_state()
    loop = GameLoop(current_state)
    drawer = Drawer(current_state.environment.map.get_width(),
                    current_state.environment.map.get_height())
    drawer.draw(current_state)

    while current_state.is_running and current_state.player.stats.health > 0:
        drawer.draw(current_state)
        key = KeyboardInterpreter.get_next_key()
        current_state = loop.run_game_turn(key)
