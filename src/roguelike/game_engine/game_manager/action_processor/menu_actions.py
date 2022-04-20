"""Contains functions performing menu actions and their factory"""
import typing as tp

from roguelike.game_engine.game_manager.game_processor.game_state import GameState, Key


def _exit(state: GameState) -> None:
    state.is_running = False


class MenuActionFactory:
    """Produces general actions that can be performed in any mode"""
    def __init__(self) -> None:
        self._special_keys = {Key.Q}

    def is_valid_key(self, key: Key) -> bool:
        return key in self._special_keys

    def get_action(self, _: Key) -> tp.Callable[[GameState], None]:
        return _exit
