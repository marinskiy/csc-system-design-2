"""
Contains game main loop
"""

import os

from roguelike.game_engine.game_manager.game_constructor.game_loader import GameLoader
from roguelike.game_engine.game_manager.game_processor.game_loop import GameLoop
from roguelike.ui.drawer import Drawer
from roguelike.ui.keyboard_interpreter import KeyboardInterpreter

DEFAULT_MAP = os.path.join('assets', 'maps', 'forest.json')

if __name__ == '__main__':
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), DEFAULT_MAP)
    current_state = GameLoader.load_game(file_path)
    loop = GameLoop(current_state)
    drawer = Drawer(*current_state.environment.map.get_dimensions())
    drawer.draw(current_state)

    while current_state.is_running and current_state.player.stats.health:
        key = KeyboardInterpreter.get_next_key()
        current_state = loop.run_game_turn(key)
        drawer.draw(current_state)
