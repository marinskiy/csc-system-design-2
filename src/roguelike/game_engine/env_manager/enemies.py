"""This module contains classes for enemies"""
from random import randrange
from abc import abstractmethod
import typing as tp


from .map_objects_storage import Creature, Stats, Obstacle, PlayerCharacter
from .map import MapCoordinates, Map


class Behaviour:
    pass


class NPC(Creature):
    """The parent class for enemies"""
    def __init__(self, level: int, stats: Stats, radius: int) -> None:
        super().__init__(level, stats)
        self._action_radius = radius

    @abstractmethod
    def act(self, geomap: Map, player: PlayerCharacter) -> None:
        pass


class Mob(NPC):
    """Normal enemy"""
    def __init__(self, level: int, stats: Stats, radius: int, behaviour: Behaviour) -> None:
        super().__init__(level, stats, radius)
        self._behaviour = behaviour

    def act(self, geomap: Map, player: PlayerCharacter) -> None:
        pass


class ConfusedMob(NPC):
    """Enemy in a confused state"""
    def __init__(self, normal_mob: NPC, timeout: int, callback: tp.Callable[[], None]) -> None:
        super().__init__(1, normal_mob.stats, 0)
        if isinstance(normal_mob, ConfusedMob):
            self._normal = normal_mob._get_normal()
        else:
            self._normal = normal_mob
        self._timeout = timeout
        self._final_action = callback

    def _get_normal(self) -> NPC:
        return self._normal

    def _act_confused(self, geomap: Map, coordinates: MapCoordinates) -> None:
        new_coordinates = coordinates.get_neighbours()[randrange(4)]
        items = geomap.get_objects(new_coordinates)

        if Obstacle() in items:
            return
        for item in items:
            if isinstance(item, Creature):
                return
        geomap.move_to(self, new_coordinates)

    def act(self, geomap: Map, player: PlayerCharacter) -> None:
        coordinates = geomap.get_coordinates(self)
        if coordinates is None:
            raise RuntimeError

        self._act_confused(geomap, coordinates)

        self._timeout -= 1
        if self._timeout == 0:
            self._final_action()

    def take_damage(self, power: int) -> None:
        super().take_damage(power)
        self._normal.take_damage(power)
