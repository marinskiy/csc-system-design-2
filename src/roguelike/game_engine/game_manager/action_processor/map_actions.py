"""Contains functions performing map actions and their factory"""

from roguelike.game_engine.env_manager import Map, MapCoordinates, MapObject, map_objects_storage
from .bases import BaseAction, BaseActionFactory
from ..game_processor.game_state import GameState, Key, Mode


class SwitchToInventoryAction(BaseAction):
    @staticmethod
    def __call__(state: GameState) -> None:
        state.mode = Mode.INVENTORY


def _get_player_coordinates(state: GameState) -> MapCoordinates:
    coordinates = state.environment.map.get_coordinates(state.player)
    if coordinates is None:
        raise RuntimeError("No player on map")
    return coordinates


class TakeTreasuresAction(BaseAction):
    @staticmethod
    def __call__(state: GameState) -> None:
        coordinates = _get_player_coordinates(state)
        items = state.environment.map.get_objects(coordinates)
        for item in items:
            if isinstance(item, map_objects_storage.Treasure):
                state.environment.map.remove_object(item)
                state.inventory.add_treasure(item)


def _move_item_to(geomap: Map, map_object: MapObject, coordinates: MapCoordinates) -> None:
    for item in geomap.get_objects(coordinates):
        if isinstance(item, map_objects_storage.Obstacle):
            return
    geomap.move_to(map_object, coordinates)


class MoveRightAction(BaseAction):
    @staticmethod
    def __call__(state: GameState) -> None:
        coordinates = _get_player_coordinates(state)
        _move_item_to(state.environment.map, state.player, MapCoordinates(coordinates.x + 1, coordinates.y))


class MoveLeftAction(BaseAction):
    @staticmethod
    def __call__(state: GameState) -> None:
        coordinates = _get_player_coordinates(state)
        _move_item_to(state.environment.map, state.player, MapCoordinates(coordinates.x - 1, coordinates.y))


class MoveUpAction(BaseAction):
    @staticmethod
    def __call__(state: GameState) -> None:
        coordinates = _get_player_coordinates(state)
        _move_item_to(state.environment.map, state.player, MapCoordinates(coordinates.x, coordinates.y - 1))


class MoveDownAction(BaseAction):
    @staticmethod
    def __call__(state: GameState) -> None:
        coordinates = _get_player_coordinates(state)
        _move_item_to(state.environment.map, state.player, MapCoordinates(coordinates.x, coordinates.y + 1))


class MapActionFactory(BaseActionFactory):
    """Produces actions in map mode"""

    def __init__(self) -> None:
        self._actions = {
            Key.D: MoveRightAction(),
            Key.A: MoveLeftAction(),
            Key.W: MoveUpAction(),
            Key.S: MoveDownAction(),
            Key.E: TakeTreasuresAction(),
            Key.II: SwitchToInventoryAction(),
        }

    def is_valid_key(self, key: Key) -> bool:
        return key in self._actions

    def get_action(self, key: Key) -> BaseAction:
        return self._actions[key]
