"""
Contains game main loop
"""

import os
import argparse
import typing as tp

from roguelike.game_engine.game_manager import GameLoop, GameLoader
from roguelike.game_engine.game_manager.game_constructor.game_generator import GameGenerator
from roguelike.game_engine.game_manager.game_processor.game_state import GameState
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
    if args.path is not None:
        return GameLoader.load_game(args.path)
    else:
        return GameGenerator().generate()


if __name__ == "__main__":
    current_state = get_game_state()
    loop = GameLoop(current_state)

    while current_state.is_running and current_state.player.stats.health:
        key = KeyboardInterpreter.get_next_key()
        current_state = loop.run_game_turn(key)
