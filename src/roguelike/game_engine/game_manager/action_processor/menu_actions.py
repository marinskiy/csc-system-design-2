"""Contains functions performing menu actions and their factory"""

from .bases import BaseAction, BaseActionFactory
from ..game_processor.game_state import GameState, Key


class ExitAction(BaseAction):
    @staticmethod
    def __call__(state: GameState) -> None:
        state.is_running = False


class MenuActionFactory(BaseActionFactory):
    """Produces general actions that can be performed in any mode"""
    def __init__(self) -> None:
        self._special_keys = {Key.Q: ExitAction()}

    def is_valid_key(self, key: Key) -> bool:
        return key in self._special_keys

    def get_action(self, key: Key) -> BaseAction:
        return self._special_keys[key]
