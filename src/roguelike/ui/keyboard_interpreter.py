"""Contains class and function for interpreting keyboard input"""

import keyboard

from roguelike.game_engine.game_manager.game_processor.game_state import Key


class KeyboardInterpreter:
    """Gets keyboard input from player"""

    @staticmethod
    def get_next_key() -> Key:
        while True:
            pressed_button = keyboard.read_key()
            try:
                return Key(pressed_button)
            except ValueError:
                pass
