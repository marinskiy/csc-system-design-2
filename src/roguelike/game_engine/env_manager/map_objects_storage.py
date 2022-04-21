"""
Contains classes for entities that can be placed on the map.
All those objects must inherit from `MapObject` class.

Some objects may have `Stats` for changing owner characteristics.
"""

from dataclasses import dataclass
import typing as tp


class MapObject:
    pass


class Obstacle(MapObject):
    pass


@dataclass
class Stats:
    health: float
    attack: float

    def __add__(self, other: tp.Any) -> 'Stats':
        if isinstance(other, Stats):
            return Stats(self.health + other.health, self.attack + other.attack)
        else:
            raise NotImplementedError('Summation with unknown type.')


class PlayerCharacter(MapObject):
    def __init__(self, stats: Stats) -> None:
        super().__init__()
        self._stats = stats

    @property
    def stats(self) -> Stats:
        return self._stats


class Treasure(MapObject):
    """Class for describing treasure that can enhance owner's stats"""

    def __init__(self, name: str, stats: Stats) -> None:
        super().__init__()
        self._name = name
        self._stats = stats

    @property
    def stats(self) -> Stats:
        return self._stats

    @property
    def name(self) -> str:
        return self._name
