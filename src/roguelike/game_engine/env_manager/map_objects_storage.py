"""
Contains classes for entities that can be placed on the map.
All those objects must inherit from `MapObject` class.

Some objects may have `Stats` for changing owner characteristics.
"""

import typing as tp
from dataclasses import dataclass

from PIL import Image, ImageDraw

from roguelike.ui.drawable import Drawable

__all__ = ['MapObject', 'Treasure', 'Obstacle', 'PlayerCharacter', 'Creature', 'Stats']


class MapObject(Drawable):
    pass


class Obstacle(MapObject):
    def draw(self, width: int, height: int) -> Image:
        return Image.new('RGB', (width, height), 'blue')


@dataclass
class Stats:
    """Stats class"""

    health: int
    attack: int

    def __add__(self, other: tp.Any) -> 'Stats':
        if isinstance(other, Stats):
            return Stats(self.health + other.health, self.attack + other.attack)
        else:
            raise NotImplementedError('Summation with unknown type.')


class Creature(MapObject):
    """The parent class for all objects capable of action"""
    def __init__(self, level: int, stats: Stats) -> None:
        super().__init__()
        self._stats = stats
        self._level = level

    @property
    def attack_power(self) -> int:
        return self._stats.attack

    def take_damage(self, power: int) -> None:
        self._stats.health -= power

    @property
    def level(self) -> int:
        return self._level

    def is_dead(self) -> int:
        return self._stats.health < 0

    @property
    def stats(self) -> Stats:
        return self._stats


class PlayerCharacter(Creature):
    """Player Object"""

    def __init__(self, stats: Stats) -> None:
        super().__init__(1, stats)

    def gain_experience(self, experience: int) -> None:
        pass

    def draw(self, width: int, height: int) -> Image:
        return Image.new('RGB', (width, height), 'purple')


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

    def draw(self, width: int, height: int) -> Image:
        img = Image.new('RGB', (width, height), 'cyan')
        draw = ImageDraw.Draw(img)
        text = f'{int(self._stats.attack)}/{int(self._stats.health)}'
        textwidth, textheight = draw.textsize(text)
        x = (width - textwidth) // 2
        y = (height - textheight) // 2
        draw.text((x, y), text)
        return img
