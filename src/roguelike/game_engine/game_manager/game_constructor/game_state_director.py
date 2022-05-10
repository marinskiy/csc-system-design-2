"""
Contains all classes needed for GameStateDirector
"""

import typing as tp
from abc import abstractmethod

from roguelike.game_engine.env_manager import Map, MapCoordinates
from roguelike.game_engine.env_manager.enemies import NPC
from roguelike.game_engine.env_manager.env_manager import SupportsNpcProtocol, Environment, Inventory
from roguelike.game_engine.env_manager.map_objects_storage import PlayerCharacter, MapObject
from roguelike.game_engine.game_manager.game_processor.game_state import GameState, Mode


class GameStateBuilder:
    @abstractmethod
    def build(self) -> tp.Tuple[Map, tp.List[tp.Tuple[MapObject, MapCoordinates]]]:
        pass


class GameStateDirector:
    """Produces GameState using provided builder"""

    def __init__(self, builder: GameStateBuilder) -> None:
        self._builder = builder

    def construct(self) -> GameState:
        geomap, world_objects_with_coords = self._builder.build()

        enemies: tp.Set[SupportsNpcProtocol] = set()
        player = None

        for world_object, coords in world_objects_with_coords:
            if isinstance(world_object, PlayerCharacter):
                player = world_object
            if isinstance(world_object, NPC):
                enemies.add(world_object)
            geomap.add_object(coords, world_object)

        if player is None:
            raise RuntimeError("There is no player in world_objects")

        return GameState(Mode.MAP, Environment(geomap, enemies), Inventory([]), player)
