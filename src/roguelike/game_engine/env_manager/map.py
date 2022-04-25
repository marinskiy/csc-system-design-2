"""Contains all classes to manage Map entity"""
from __future__ import annotations

import typing as tp
from dataclasses import dataclass
from itertools import product

from PIL import Image

from roguelike.game_engine.env_manager.map_objects_storage import MapObject
from roguelike.ui.drawable import Drawable, load_image_resource
from roguelike.game_engine.env_manager.shortest_path_searchers import search_using_a_star


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

    def __lt__(self, other: tp.Any) -> bool:
        if isinstance(other, MapCoordinates):
            if self.x < other.x:
                return True
            if self.y < other.y:
                return True
            return False
        else:
            raise NotImplementedError

    @property
    def left(self) -> MapCoordinates:
        return MapCoordinates(self.x - 1, self.y)

    @property
    def right(self) -> MapCoordinates:
        return MapCoordinates(self.x + 1, self.y)

    @property
    def up(self) -> MapCoordinates:
        return MapCoordinates(self.x, self.y + 1)

    @property
    def down(self) -> MapCoordinates:
        return MapCoordinates(self.x, self.y - 1)


class MapCell:
    """Stores items for given map cell"""

    def __init__(self) -> None:
        self._items: tp.Set[MapObject] = set()

    def add(self, object_id: MapObject) -> None:
        self._items.add(object_id)

    def remove(self, object_id: MapObject) -> None:
        self._items.remove(object_id)

    @property
    def items(self) -> tp.Collection[MapObject]:
        return tuple(self._items)


class Map(Drawable):
    """Container for interacting with objects on the map"""

    def __init__(self, map_width: int, map_height: int) -> None:
        self._validate_map_size(map_width, map_height)
        self._height = map_height
        self._width = map_width
        self._coord_to_cell: tp.Dict[MapCoordinates, MapCell] = {
            MapCoordinates(x, y): MapCell()
            for x, y in product(range(map_width), range(map_height))
        }
        self._map_object_to_coord: tp.Dict[MapObject, MapCoordinates] = {}

    @staticmethod
    def _validate_map_size(map_width: int, map_height: int) -> None:
        if map_width < 1 or map_height < 1:
            raise ValueError('Invalid map size. Must be at least 1x1.')

    def _are_valid_coordinates(self, coordinates: MapCoordinates) -> bool:
        x_within_bounds = 0 <= coordinates.x < self._width
        y_within_bounds = 0 <= coordinates.y < self._height
        return x_within_bounds and y_within_bounds

    def _is_on_the_map(self, map_object: MapObject) -> bool:
        return map_object in self._map_object_to_coord

    def move_to(self, map_object: MapObject, coordinates: MapCoordinates) -> None:
        if not self._are_valid_coordinates(coordinates) or not self._is_on_the_map(map_object):
            return
        self._coord_to_cell[coordinates].add(map_object)
        old_coordinates = self._map_object_to_coord.pop(map_object)
        self._coord_to_cell[old_coordinates].remove(map_object)
        self._map_object_to_coord[map_object] = coordinates

    def get_objects(self, coordinates: MapCoordinates) -> tp.Collection[MapObject]:
        if not self._are_valid_coordinates(coordinates):
            return ()
        return self._coord_to_cell[coordinates].items

    def add_object(self, coordinates: MapCoordinates, map_object: MapObject) -> None:
        if not self._are_valid_coordinates(coordinates):
            return
        if self._is_on_the_map(map_object):
            raise ValueError('Adding object that is already on the map')
        self._coord_to_cell[coordinates].add(map_object)
        self._map_object_to_coord[map_object] = coordinates

    def remove_object(self, map_object: MapObject) -> None:
        if not self._is_on_the_map(map_object):
            return
        coordinates = self._map_object_to_coord.pop(map_object)
        self._coord_to_cell[coordinates].remove(map_object)

    def get_coordinates(self, map_object: MapObject) -> tp.Optional[MapCoordinates]:
        if not self._is_on_the_map(map_object):
            return None
        return self._map_object_to_coord[map_object]

    def _draw_map_cell(self, coordinates: MapCoordinates, size: int) -> Image:
        objs = list(self.get_objects(coordinates))
        if objs:
            return objs[-1].draw(size, size)
        return load_image_resource('grass.png', size, size)

    def draw(self, width: int, height: int) -> Image:
        cell_size = width // self._width
        assert width % self._width == height % self._height
        assert width // self._width == height // self._height
        map_image = Image.new('RGB', (width, height))
        for x_coordinate in range(self._width):
            for y_coordinate in range(self._height):
                map_coordinates = MapCoordinates(x_coordinate, y_coordinate)
                map_image.paste(
                    self._draw_map_cell(map_coordinates, cell_size),
                    (x_coordinate * cell_size,
                     # this is done due to img rendering from upper left conner
                     (self._height - y_coordinate - 1) * cell_size),
                )
        return map_image

    def get_width(self) -> int:
        return self._width

    def get_height(self) -> int:
        return self._height

    def get_neighbours(
            self, coordinates: MapCoordinates,
    ) -> tp.Tuple[MapCoordinates, ...]:
        valid_neighbours = []
        if coordinates.x > 0:
            valid_neighbours.append(coordinates.left)
        if coordinates.y > 0:
            valid_neighbours.append(coordinates.down)
        if coordinates.x < self._width - 1:
            valid_neighbours.append(coordinates.right)
        if coordinates.y < self._height - 1:
            valid_neighbours.append(coordinates.up)
        return tuple(valid_neighbours)

    def get_distance_between_coordinates(self, coordinates_first: MapCoordinates,
                                         coordinates_second: MapCoordinates) -> int:
        _, distance_to_coordinates = search_using_a_star(self, coordinates_first, coordinates_second)
        return distance_to_coordinates[coordinates_second]

    def get_distance_between_objects(self, object_first: MapObject, object_second: MapObject) -> int:
        coordinates_first = self.get_coordinates(object_first)
        if coordinates_first is None:
            raise ValueError(f'Can\'t find {object_first}')
        coordinates_second = self.get_coordinates(object_second)
        if coordinates_second is None:
            raise ValueError(f'Can\'t find {object_second}')
        return self.get_distance_between_coordinates(coordinates_first, coordinates_second)
