"""This module contains classes for enemies"""
import random

import typing as tp
from abc import abstractmethod
from enum import Enum, auto

from .map import MapCoordinates, Map
from .map_objects_storage import Creature, Stats, Obstacle, PlayerCharacter
from roguelike.ui.drawable import drawable


class CreatureMove(Enum):
    MOVE_AWAY = auto()
    MOVE_CLOSER = auto()


def _coord_has_objects_of_types(target_coords: MapCoordinates, geomap: Map, target_types: tp.List[tp.Any]) -> bool:
    items = geomap.get_objects(target_coords)
    for item in items:
        if isinstance(item, tuple(target_types)):
            return True
    return False


def _get_all_possible_creature_move_coords(actor_coords: MapCoordinates, geomap: Map,
                                           banned_types: tp.List[tp.Any]) -> tp.List[MapCoordinates]:
    possible_coordinates: tp.List[MapCoordinates] = []

    neighbour_coords_list = geomap.get_neighbours(actor_coords)
    for neighbour_coords in neighbour_coords_list:
        if not _coord_has_objects_of_types(neighbour_coords, geomap, banned_types):
            possible_coordinates.append(neighbour_coords)

    return possible_coordinates


def _get_possible_creature_moves(move_type: CreatureMove, actor: 'Mob',
                                 geomap: Map, player: PlayerCharacter) -> tp.List[MapCoordinates]:
    actor_coords = geomap.get_coordinates(actor)
    if not isinstance(actor_coords, MapCoordinates):
        raise ValueError('Actor is not on the map')
    player_coords = geomap.get_coordinates(player)
    if not isinstance(player_coords, MapCoordinates):
        raise ValueError('Player is not on the map')
    distance = geomap.get_distance_between_objects(actor, player)
    all_possible_moves = _get_all_possible_creature_move_coords(actor_coords, geomap, [Obstacle, NPC])

    if move_type == CreatureMove.MOVE_AWAY:
        return [coord for coord in all_possible_moves if
                geomap.get_distance_between_coordinates(coord, player_coords) > distance]
    if move_type == CreatureMove.MOVE_CLOSER:
        return [coord for coord in all_possible_moves if
                geomap.get_distance_between_coordinates(coord, player_coords) < distance]
    return []


def _attack_player(actor: 'Mob', player: PlayerCharacter) -> None:
    player.take_damage(actor.attack_power)


def _move_creature_to(actor: 'Mob', geomap: Map, player: PlayerCharacter, new_coordinates: MapCoordinates) -> None:
    if _coord_has_objects_of_types(new_coordinates, geomap, [Obstacle, NPC]):
        return
    if _coord_has_objects_of_types(new_coordinates, geomap, [PlayerCharacter]):
        _attack_player(actor, player)
        return

    geomap.move_to(actor, new_coordinates)


class Behaviour:
    """Class that is responsible for mob's behaviour"""

    @staticmethod
    def _check_player_in_action_radius(actor: 'Mob', geomap: Map, player: PlayerCharacter) -> bool:
        distance = geomap.get_distance_between_objects(actor, player)
        if distance > actor.action_radius:
            return False
        return True

    def act(self, actor: 'Mob', geomap: Map, player: PlayerCharacter) -> None:
        if not self._check_player_in_action_radius(actor, geomap, player):
            return

        possible_moves = self._get_possible_moves(actor, geomap, player)
        if len(possible_moves) == 0:
            return

        new_coordinates = random.choice(possible_moves)
        _move_creature_to(actor, geomap, player, new_coordinates)

    @abstractmethod
    def _get_possible_moves(self, actor: 'Mob', geomap: Map, player: PlayerCharacter) -> tp.List[MapCoordinates]:
        pass


class AggressiveBehaviour(Behaviour):
    def _get_possible_moves(self, actor: 'Mob', geomap: Map, player: PlayerCharacter) -> tp.List[MapCoordinates]:
        return _get_possible_creature_moves(CreatureMove.MOVE_CLOSER, actor, geomap, player)


class CowardlyBehaviour(Behaviour):
    def _get_possible_moves(self, actor: 'Mob', geomap: Map, player: PlayerCharacter) -> tp.List[MapCoordinates]:
        return _get_possible_creature_moves(CreatureMove.MOVE_AWAY, actor, geomap, player)


class PassiveBehaviour(Behaviour):
    def _get_possible_moves(self, actor: 'Mob', geomap: Map, player: PlayerCharacter) -> tp.List[MapCoordinates]:
        return []


class BehaviourFactory:
    """Produces behaviours of mobs"""

    _behaviours = {
        'aggressive': AggressiveBehaviour(),
        'cowardly': CowardlyBehaviour(),
        'passive': PassiveBehaviour()
    }

    @classmethod
    def is_valid_key(cls, key: str) -> bool:
        return key in cls._behaviours

    @classmethod
    def get_behaviour(cls, key: str) -> Behaviour:
        return cls._behaviours[key]


class NPC(Creature):
    """The parent class for enemies"""

    def __init__(self, level: int, stats: Stats, radius: int) -> None:
        super().__init__(level, stats)
        self._action_radius = radius

    @abstractmethod
    def act(self, geomap: Map, player: PlayerCharacter) -> None:
        pass

    @property
    def action_radius(self) -> int:
        return self._action_radius


@drawable('demon.png')
class Mob(NPC):
    """Normal enemy"""

    def __init__(self, level: int, stats: Stats, radius: int, behaviour: Behaviour) -> None:
        super().__init__(level, stats, radius)
        self._behaviour = behaviour

    def act(self, geomap: Map, player: PlayerCharacter) -> None:
        self._behaviour.act(self, geomap, player)


@drawable('pepe.png')
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
        possible_coordinates = geomap.get_neighbours(coordinates)
        new_coordinates = random.choice(possible_coordinates)
        if _coord_has_objects_of_types(new_coordinates, geomap, [Creature, Obstacle]):
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
