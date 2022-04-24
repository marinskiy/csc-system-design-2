"""Contains functions performing map actions and their factory"""

import typing as tp
from random import randrange

from ....game_engine.env_manager import Map, MapCoordinates, MapObject, map_objects_storage, Environment
from ....game_engine.env_manager.enemies import NPC, ConfusedMob
from .bases import BaseAction, BaseActionFactory
from ..game_processor.game_state import GameState, Key, Mode


class SwitchToInventoryAction(BaseAction):
    @staticmethod
    def __call__(state: GameState) -> None:
        state.mode = Mode.INVENTORY


def _get_player_coordinates(state: GameState) -> MapCoordinates:
    coordinates = state.environment.map.get_coordinates(state.player)
    if coordinates is None:
        raise RuntimeError("No player on map")
    return coordinates


class TakeTreasuresAction(BaseAction):
    @staticmethod
    def __call__(state: GameState) -> None:
        coordinates = _get_player_coordinates(state)
        items = state.environment.map.get_objects(coordinates)
        for item in items:
            if isinstance(item, map_objects_storage.Treasure):
                state.environment.map.remove_object(item)
                state.inventory.add_treasure(item)


def _get_blocking_object(geomap: Map, coordinates: MapCoordinates) -> tp.Optional[MapObject]:
    for item in geomap.get_objects(coordinates):
        if isinstance(item, (map_objects_storage.Obstacle, map_objects_storage.Creature)):
            return item
    return None


def _attack_creature(
        environment: Environment, player: map_objects_storage.PlayerCharacter,
        npc: NPC, coordinates: MapCoordinates) -> None:
    critical_hit = randrange(10)
    if critical_hit == 0:
        npc.take_damage(2 * player.attack_power)
    else:
        npc.take_damage(player.attack_power)

    if npc.is_dead():
        environment.map.remove_object(npc)
        environment.enemies.remove(npc)

        player.gain_experience(npc.level)
        return

    if critical_hit == 1:
        def callback() -> None:
            coordinates = environment.map.get_coordinates(confused)
            if coordinates is None:
                raise RuntimeError
            environment.map.remove_object(confused)
            environment.enemies.remove(confused)
            environment.map.add_object(coordinates, npc)
            environment.enemies.add(npc)

        confused = ConfusedMob(npc, 3, callback)
        environment.map.remove_object(npc)
        environment.enemies.remove(npc)
        environment.map.add_object(coordinates, confused)
        environment.enemies.add(confused)


def _move_player_to(environment: Environment,
                    player: map_objects_storage.PlayerCharacter,
                    coordinates: MapCoordinates) -> None:
    block = _get_blocking_object(environment.map, coordinates)
    if isinstance(block, map_objects_storage.Obstacle):
        return
    if isinstance(block, NPC):
        _attack_creature(environment, player, block, coordinates)
        return

    environment.map.move_to(player, coordinates)


class MoveRightAction(BaseAction):
    @staticmethod
    def __call__(state: GameState) -> None:
        coordinates = _get_player_coordinates(state)
        _move_player_to(state.environment, state.player, coordinates.right)


class MoveLeftAction(BaseAction):
    @staticmethod
    def __call__(state: GameState) -> None:
        coordinates = _get_player_coordinates(state)
        _move_player_to(state.environment, state.player, coordinates.left)


class MoveUpAction(BaseAction):
    @staticmethod
    def __call__(state: GameState) -> None:
        coordinates = _get_player_coordinates(state)
        _move_player_to(state.environment, state.player, coordinates.up)


class MoveDownAction(BaseAction):
    @staticmethod
    def __call__(state: GameState) -> None:
        coordinates = _get_player_coordinates(state)
        _move_player_to(state.environment, state.player, coordinates.down)


class MapActionFactory(BaseActionFactory):
    """Produces actions in map mode"""

    def __init__(self) -> None:
        self._actions = {
            Key.D: MoveRightAction(),
            Key.A: MoveLeftAction(),
            Key.W: MoveUpAction(),
            Key.S: MoveDownAction(),
            Key.E: TakeTreasuresAction(),
            Key.II: SwitchToInventoryAction(),
        }

    def is_valid_key(self, key: Key) -> bool:
        return key in self._actions

    def get_action(self, key: Key) -> BaseAction:
        return self._actions[key]
