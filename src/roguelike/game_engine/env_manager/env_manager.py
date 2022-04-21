"""Contains high level classes for managing environment"""

import typing as tp
from dataclasses import dataclass

from . import map_objects_storage
from .map import Map


class Drawable:
    pass


class InventoryPresenter(Drawable):
    """Class that governs the presentation of the Inventory"""

    def __init__(self, treasures: tp.Iterable[map_objects_storage.Treasure]) -> None:
        self._treasures = list(treasures)
        self._current = 0

    def add_treasure(self, treasure: map_objects_storage.Treasure) -> None:
        self._treasures.append(treasure)

    def select_next(self) -> None:
        if self._current + 1 < len(self._treasures):
            self._current += 1

    def select_previous(self) -> None:
        if self._current > 0:
            self._current -= 1

    def get_selected(self) -> tp.Optional[map_objects_storage.Treasure]:
        if self._treasures:
            return self._treasures[self._current]
        return None


class Inventory:
    """Class for describing player's inventory"""

    def __init__(self, treasures: tp.Iterable[map_objects_storage.Treasure]) -> None:
        self._treasure_is_worn = {treasure: False for treasure in treasures}
        self._presenter = InventoryPresenter(treasures)

    def get_additional_stats(self) -> map_objects_storage.Stats:
        return sum((treasure.stats
                    for treasure, is_on in self._treasure_is_worn.items()
                    if is_on), start=map_objects_storage.Stats(0.0, 0.0))

    def change_treasure_state(self, treasure: map_objects_storage.Treasure) -> None:
        self._treasure_is_worn[treasure] = not self._treasure_is_worn[treasure]

    def get_treasures(self) -> tp.Iterable[map_objects_storage.Treasure]:
        return tuple(self._treasure_is_worn)

    def add_treasure(self, treasure: map_objects_storage.Treasure) -> None:
        self._treasure_is_worn[treasure] = False
        self._presenter.add_treasure(treasure)

    @property
    def presenter(self) -> InventoryPresenter:
        return self._presenter


@dataclass
class Environment:
    map: Map
    world_objects: tp.List[map_objects_storage.MapObject]
