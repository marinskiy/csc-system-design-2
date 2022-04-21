"""Contains main class for generation and performance of game actions"""
import typing as tp

from roguelike.game_engine.game_manager.game_processor.game_state import GameState, Key, Mode
from roguelike.game_engine.game_manager.action_processor.map_actions import MapActionFactory
from roguelike.game_engine.game_manager.action_processor.inventory_actions import InventoryActionFactory
from roguelike.game_engine.game_manager.action_processor.menu_actions import MenuActionFactory


def _no_action(_: GameState) -> None:
    pass


class ActionManager:
    """Produces functions that act on GameState provided key and state"""
    def __init__(self) -> None:
        self._map_factory = MapActionFactory()
        self._inventory_factory = InventoryActionFactory()
        self._menu_factory = MenuActionFactory()

    def get_action(self, key: Key, state: GameState) -> tp.Callable[[GameState], None]:
        if self._menu_factory.is_valid_key(key):
            return self._menu_factory.get_action(key)
        if state.mode == Mode.MAP and self._map_factory.is_valid_key(key):
            return self._map_factory.get_action(key)
        elif state.mode == Mode.INVENTORY and self._inventory_factory.is_valid_key(key):
            return self._inventory_factory.get_action(key)
        return _no_action
