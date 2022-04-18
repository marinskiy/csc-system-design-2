"""Contains functions performing map actions and their factory"""
import typing as tp

from roguelike.game_engine.game_manager.game_processor.game_state import GameState, Key, Mode
from roguelike.game_engine.env_manager.map_objects_storage import Treasure, Obstacle
from roguelike.game_engine.env_manager.map import Map, MapCoordinates, MapObject


def _switch_to_inventory(state: GameState) -> None:
    state.mode = Mode.INVENTORY


def _get_player_coordinates(state: GameState) -> MapCoordinates:
    coordinates = state.environment.map.get_coordinates(state.player)
    if not coordinates:
        raise RuntimeError("No player on map")
    return coordinates


def _take_treasures(state: GameState) -> None:
    coordinates = _get_player_coordinates(state)
    items = state.environment.map.get_objects(coordinates)
    for item in items:
        if isinstance(item, Treasure):
            state.environment.map.remove_object(item)
            state.inventory.add_treasure(item)


def _move_item_to(geomap: Map, map_object: MapObject, coordinates: MapCoordinates) -> None:
    for item in geomap.get_objects(coordinates):
        if isinstance(item, Obstacle):
            return
    geomap.move_to(map_object, coordinates)


def _move_right(state: GameState) -> None:
    coordinates = _get_player_coordinates(state)
    _move_item_to(state.environment.map, state.player, MapCoordinates(coordinates.x + 1, coordinates.y))


def _move_left(state: GameState) -> None:
    coordinates = _get_player_coordinates(state)
    _move_item_to(state.environment.map, state.player, MapCoordinates(coordinates.x - 1, coordinates.y))


def _move_up(state: GameState) -> None:
    coordinates = _get_player_coordinates(state)
    _move_item_to(state.environment.map, state.player, MapCoordinates(coordinates.x, coordinates.y - 1))


def _move_down(state: GameState) -> None:
    coordinates = _get_player_coordinates(state)
    _move_item_to(state.environment.map, state.player, MapCoordinates(coordinates.x, coordinates.y + 1))


class MapActionFactory:
    """Produces actions in map mode"""
    def __init__(self) -> None:
        self.actions = {
            Key.D: _move_right,
            Key.A: _move_left,
            Key.W: _move_up,
            Key.S: _move_down,
            Key.E: _take_treasures,
            Key.II: _switch_to_inventory,
        }

    def valid_key(self, key: Key) -> bool:
        return key in self.actions

    def get(self, key: Key) -> tp.Callable[[GameState], None]:
        return self.actions[key]
