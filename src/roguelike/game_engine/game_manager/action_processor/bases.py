"""Contains Action and ActionFactory interfaces"""
from abc import abstractmethod

from ..game_processor.game_state import GameState, Key


class BaseAction:
    @staticmethod
    @abstractmethod
    def __call__(game_state: GameState) -> None:
        pass


class BaseActionFactory:
    @abstractmethod
    def is_valid_key(self, key: Key) -> bool:
        pass

    @abstractmethod
    def get_action(self, key: Key) -> BaseAction:
        pass
