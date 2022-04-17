"""Contains functions performing inventory actions and their factory"""
import typing as tp

from roguelike.game_engine.game_manager.game_processor.game_state import GameState, Key, Mode


def _switch_to_map(state: GameState) -> None:
    state.mode = Mode.MAP


def _change_treasure_state(state: GameState) -> None:
    treasure = state.inventory.presenter.get_selected()
    if treasure:
        state.inventory.change_treasure_state(treasure)


def _select_next(state: GameState) -> None:
    state.inventory.presenter.select_next()


def _select_previous(state: GameState) -> None:
    state.inventory.presenter.select_previous()


class InventoryActionFactory:
    """Produces actions in inventory mode"""
    def __init__(self) -> None:
        self.actions = {
            Key.W: _select_previous,
            Key.S: _select_next,
            Key.E: _change_treasure_state,
            Key.M: _switch_to_map,
        }

    def valid_key(self, key: Key) -> bool:
        return key in self.actions

    def get(self, key: Key) -> tp.Callable[[GameState], None]:
        return self.actions[key]
