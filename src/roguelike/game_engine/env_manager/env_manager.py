"""Contains high level classes for managing environment"""

import typing as tp
from dataclasses import dataclass

from roguelike.game_engine.env_manager.map import Map
from roguelike.game_engine.env_manager.map_objects_storage import Treasure, MapObject, Stats


class Inventory:
    """Class for describing player's inventory"""

    def __init__(self, treasures: tp.List[Treasure]) -> None:
        self._treasure_is_worn = {treasure: False for treasure in treasures}

    def get_additional_stats(self) -> Stats:
        final_stats = sum(treasure.stats
                          for treasure, is_on in self._treasure_is_worn.items()
                          if is_on)
        return tp.cast(Stats, final_stats)

    def put_on(self, treasure: Treasure) -> None:
        self._treasure_is_worn[treasure] = True

    def put_off(self, treasure: Treasure) -> None:
        self._treasure_is_worn[treasure] = False

    def get_treasures(self) -> tp.Iterable[Treasure]:
        return tuple(self._treasure_is_worn)


@dataclass
class Environment:
    map: Map
    world_objects: tp.List[MapObject]
