"""Contains functions performing inventory actions and their factory"""

from roguelike.game_engine.game_manager.action_processor.bases import BaseAction, BaseActionFactory
from roguelike.game_engine.game_manager.game_processor.game_state import GameState, Key, Mode


class SwitchToMapAction(BaseAction):
    @staticmethod
    def __call__(state: GameState) -> None:
        state.mode = Mode.MAP


class ChangeTreasureStateAction(BaseAction):
    @staticmethod
    def __call__(state: GameState) -> None:
        treasure = state.inventory.presenter.get_selected()
        if treasure is not None:
            state.inventory.change_treasure_state(treasure)


class SelectNextAction(BaseAction):
    @staticmethod
    def __call__(state: GameState) -> None:
        state.inventory.presenter.select_next()


class SelectPreviousAction(BaseAction):
    @staticmethod
    def __call__(state: GameState) -> None:
        state.inventory.presenter.select_previous()


class InventoryActionFactory(BaseActionFactory):
    """Produces actions in inventory mode"""

    def __init__(self) -> None:
        self._actions = {
            Key.W: SelectPreviousAction(),
            Key.S: SelectNextAction(),
            Key.E: ChangeTreasureStateAction(),
            Key.M: SwitchToMapAction(),
        }

    def is_valid_key(self, key: Key) -> bool:
        return key in self._actions

    def get_action(self, key: Key) -> BaseAction:
        return self._actions[key]
