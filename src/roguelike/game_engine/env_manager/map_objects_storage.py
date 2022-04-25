"""
Contains classes for entities that can be placed on the map.
All those objects must inherit from `MapObject` class.

Some objects may have `Stats` for changing owner characteristics.
"""

import copy
import typing as tp
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

from roguelike.ui.drawable import Drawable, drawable, load_image_resource

__all__ = ['MapObject', 'Treasure', 'Obstacle', 'PlayerCharacter', 'Creature', 'Stats']


class MapObject:
    def __init__(self) -> None:
        assert isinstance(self, Drawable)

    def draw(self, width: int, height: int) -> Image:
        raise NotImplementedError()


@drawable('mountains.png')
class Obstacle(MapObject):
    pass


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


@drawable('player.png')
class PlayerCharacter(Creature):
    """Player Object"""

    def __init__(self, stats: Stats) -> None:
        super().__init__(1, stats)

    def gain_experience(self, experience: int) -> None:
        pass


class Treasure(MapObject, Drawable):
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

    def draw(self, width: int, height: int, draw_stats: bool = False) -> Image:
        img = copy.copy(load_image_resource('treasure.png', width, height))
        if not draw_stats:
            return img
        fnt = ImageFont.load_default()
        d = ImageDraw.Draw(img)

        text = f'{self._stats.attack}/{self._stats.health}'
        d.text((2, height - 15), text, font=fnt, fill=(0, 0, 0))
        return img
