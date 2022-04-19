"""Contains all classes to manage Map entity"""

import typing as tp
from dataclasses import dataclass
from itertools import product

from roguelike.game_engine.env_manager.map_objects_storage import MapObject


@dataclass
class MapCoordinates:
    """Stores map coordinates: (x, y)"""
    x: int
    y: int

    def __eq__(self, other: tp.Any) -> bool:
        if isinstance(other, MapCoordinates):
            return self.x == other.x and self.y == other.y
        return False

    def __hash__(self) -> int:
        return hash((self.x, self.y))


class MapCell:
    """Stores items for given map cell"""
    # todo: update schema
    #   new methods: add, remove
    def __init__(self) -> None:
        self._items: tp.Set[MapObject] = set()

    def add(self, object_id: MapObject) -> None:
        self._items.add(object_id)

    def remove(self, object_id: MapObject) -> None:
        self._items.remove(object_id)

    @property
    def items(self) -> tp.Collection[MapObject]:
        return tuple(self._items)


class Map:
    """Container for interacting with objects on the map"""

    def __init__(self, map_width: int, map_height: int) -> None:
        self._validate_map_size(map_height, map_width)
        self._height = map_height
        self._width = map_width
        self._coord_to_cell: tp.Dict[MapCoordinates, MapCell] = {
            MapCoordinates(x, y): MapCell()
            for x, y in product(range(map_width), range(map_height))
        }
        self._map_object_to_coord: tp.Dict[MapObject, MapCoordinates] = {}

    @staticmethod
    def _validate_map_size(map_height: int, map_width: int) -> None:
        if map_width < 1 or map_height < 1:
            raise ValueError('Invalid map size. Must be at least 1x1.')

    def _validate_coordinates(self, coordinates: MapCoordinates) -> bool:
        x, y = coordinates.x, coordinates.y
        return 0 <= x < self._width and 0 <= y < self._height

    def move_to(self, map_object: MapObject, coordinates: MapCoordinates) -> None:
        if not self._validate_coordinates(coordinates):
            return
        self._coord_to_cell[coordinates].add(map_object)
        old_coordinates = self._map_object_to_coord.pop(map_object)
        self._coord_to_cell[old_coordinates].remove(map_object)
        self._map_object_to_coord[map_object] = coordinates

    def get_objects(self, coordinates: MapCoordinates) -> tp.Collection[MapObject]:
        if not self._validate_coordinates(coordinates):
            return ()
        return self._coord_to_cell[coordinates].items

    def add_object(self, coordinates: MapCoordinates, map_object: MapObject) -> None:
        # todo: design
        #  added coordinates as arg
        if not self._validate_coordinates(coordinates):
            return
        self._coord_to_cell[coordinates].add(map_object)
        self._map_object_to_coord[map_object] = coordinates

    def remove_object(self, map_object: MapObject) -> None:
        # todo: design
        #  added coordinates as arg
        coordinates = self._map_object_to_coord.pop(map_object)
        self._coord_to_cell[coordinates].remove(map_object)

    def get_coordinates(self, map_object: MapObject) -> tp.Optional[MapCoordinates]:
        return self._map_object_to_coord.get(map_object)
