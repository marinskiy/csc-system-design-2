"""This module contains classes for enemies"""
from random import randrange
from abc import abstractmethod
from PIL import Image

from ..game_manager.action_processor.behaviours import Behaviour
from ..game_manager.game_processor.game_state import GameState
from .map_objects_storage import Creature, Stats, Obstacle
from .map import MapCoordinates


class NPC(Creature):
    """The parent class for enemies"""
    def __init__(self, level: int, stats: Stats, radius: int) -> None:
        super().__init__(level, stats)
        self._action_radius = radius

    @abstractmethod
    def act(self, state: GameState) -> None:
        pass


class Mob(NPC):
    """Normal enemy"""
    def __init__(self, level: int, stats: Stats, radius: int, behaviour: Behaviour) -> None:
        super().__init__(level, stats, radius)
        self._behaviour = behaviour

    def act(self, state: GameState) -> None:
        pass

    def draw(self, width: int, height: int) -> Image:
        return Image.new('RGB', (width, height), 'red')


class ConfusedMob(NPC):
    """Enemy in a confused state"""
    def __init__(self, normal_mob: NPC, timeout: int) -> None:
        super().__init__(1, normal_mob.stats, 0)
        self._normal = normal_mob
        self._timeout = timeout

    def _act_confused(self, state: GameState, coordinates: MapCoordinates) -> None:
        new_coordinates = coordinates.get_neighbours()[randrange(4)]
        items = state.environment.map.get_objects(new_coordinates)

        if Obstacle() in items:
            return
        for item in items:
            if isinstance(item, Creature):
                return
        state.environment.map.move_to(self, new_coordinates)

    def act(self, state: GameState) -> None:
        coordinates = state.environment.map.get_coordinates(self)
        if coordinates is None:
            raise RuntimeError

        self._act_confused(state, coordinates)

        self._timeout -= 1
        if self._timeout == 0:
            state.environment.map.remove_object(self)
            state.environment.map.add_object(coordinates, self._normal)

    def draw(self, width: int, height: int) -> Image:
        return Image.new('RGB', (width, height), 'pink')
