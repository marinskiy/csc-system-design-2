"""
Contains game main loop
"""

import os

from roguelike.game_engine.game_manager.game_constructor.game_loader import GameLoader
from roguelike.game_engine.game_manager.game_processor.game_loop import GameLoop
from roguelike.ui.keyboard_interpreter import KeyboardInterpreter

if __name__ == '__main__':
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets/maps/forest.json')
    current_state = GameLoader.load_game(file_path)
    loop = GameLoop(current_state)

    while current_state.running and current_state.player.stats.health > 0:
        key = KeyboardInterpreter.get_next_key()
        current_state = loop.run_game_turn(key)
