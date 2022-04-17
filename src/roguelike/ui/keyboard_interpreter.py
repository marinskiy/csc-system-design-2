"""Contains class and function for interpreting keyboard input"""


import typing as tp
from roguelike.game_engine.game_manager.game_processor.game_state import Key
from pynput import keyboard


key_pressed = ""


def _on_press(key: tp.Any) -> bool:
    global key_pressed

    try:
        if key.char in ("w", "a", "s", "d", "e", "i", "m", "q"):
            key_pressed = key.char
            return False
    except AttributeError:
        pass

    return True


class KeyboardInterpreter:
    """Gets keyboard input from player"""

    @staticmethod
    def get_next_key() -> Key:
        with keyboard.Listener(
                on_press=_on_press) as listener:
            listener.join()

        if key_pressed == "w":
            return Key.W
        if key_pressed == "a":
            return Key.A
        if key_pressed == "s":
            return Key.S
        if key_pressed == "d":
            return Key.D
        if key_pressed == "e":
            return Key.E
        if key_pressed == "i":
            return Key.II
        if key_pressed == "m":
            return Key.M
        else:
            return Key.Q
