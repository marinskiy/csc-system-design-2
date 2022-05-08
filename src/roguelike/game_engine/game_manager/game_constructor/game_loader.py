"""
Contains all classes needed to load game
"""

import json
import typing as tp

from roguelike.game_engine.env_manager import MapCoordinates, Map, Environment, Inventory, Stats, MapObject
from roguelike.game_engine.env_manager.enemies import Mob, BehaviourFactory, NPC
from roguelike.game_engine.env_manager.env_manager import SupportsNpcProtocol
from roguelike.game_engine.env_manager.map_objects_storage import Obstacle, Treasure, PlayerCharacter
from roguelike.game_engine.game_manager.game_processor.game_state import GameState, Mode


def check_dict_fields(value: tp.Dict[str, tp.Any], names: tp.List[str]) -> bool:
    if len(value) != len(names):
        return False
    for name in names:
        if name not in value.keys():
            return False
    return True


class GameLoader:
    """Loads GameState from file"""

    @staticmethod
    def load_game(path: str) -> GameState:
        with open(path, encoding="utf-8") as json_file:
            world_data = json.load(json_file)
        geomap, enemies, player = GameLoader._load_world(world_data)
        return GameState(Mode.MAP, Environment(geomap, enemies), Inventory([]), player)

    @staticmethod
    def _load_coordinates(value: tp.List[int]) -> MapCoordinates:
        if len(value) != 2:
            raise ValueError("Invalid coordinates json")
        return MapCoordinates(value[0], value[1])

    @staticmethod
    def _load_stats(value: tp.Dict[str, int]) -> Stats:
        if not check_dict_fields(value, ["attack", "health"]):
            raise ValueError("Invalid stats json")
        return Stats(value["health"], value["attack"])

    @staticmethod
    def _load_obstacle(value: tp.Dict[str, tp.Any]) -> Obstacle:
        if len(value) != 0:
            raise ValueError("Invalid obstacle settings json")
        return Obstacle()

    @staticmethod
    def _load_treasure(value: tp.Dict[str, tp.Any]) -> Treasure:
        if not check_dict_fields(value, ["name", "stats"]) or not isinstance(value["name"], str):
            raise ValueError("Invalid treasure settings json")
        return Treasure(value["name"], GameLoader._load_stats(value["stats"]))

    @staticmethod
    def _load_mob(value: tp.Dict[str, tp.Any]) -> Mob:
        if not check_dict_fields(value, ["level", "radius", "behaviour", "stats"]) or \
                not isinstance(value["level"], int) or not isinstance(value["radius"], int) or \
                not isinstance(value["behaviour"], str) or not BehaviourFactory.is_valid_key(value["behaviour"]):
            raise ValueError("Invalid mob settings json")

        return Mob(value["level"], GameLoader._load_stats(value["stats"]), value["radius"],
                   BehaviourFactory.get_behaviour(value["behaviour"]))

    @staticmethod
    def _load_player(value: tp.Dict[str, tp.Any]) -> PlayerCharacter:
        if not check_dict_fields(value, ["stats"]):
            raise ValueError("Invalid player settings json")
        return PlayerCharacter(GameLoader._load_stats(value["stats"]))

    @staticmethod
    def _load_map(value: tp.Dict[str, int]) -> Map:
        if not check_dict_fields(value, ["width", "height"]):
            raise ValueError("Invalid map json")
        return Map(value["width"], value["height"])

    @staticmethod
    def _load_world_object(value: tp.Dict[str, tp.Any]) -> tp.Tuple[MapObject, MapCoordinates]:
        if not check_dict_fields(value, ["type", "pos", "settings"]) or \
                value["type"] not in ["player", "obstacle", "treasure", "mob"]:
            raise ValueError("Invalid map object json format")

        coords = GameLoader._load_coordinates(value["pos"])
        world_object: MapObject

        if value["type"] == "player":
            world_object = GameLoader._load_player(value["settings"])
        elif value["type"] == "obstacle":
            world_object = GameLoader._load_obstacle(value["settings"])
        elif value["type"] == "treasure":
            world_object = GameLoader._load_treasure(value["settings"])
        elif value["type"] == "mob":
            world_object = GameLoader._load_mob(value["settings"])

        return world_object, coords

    @staticmethod
    def _load_world(value: tp.Dict[str, tp.Any]) -> tp.Tuple[Map, tp.Set[SupportsNpcProtocol], PlayerCharacter]:
        if not check_dict_fields(value, ["map", "objects"]) or not isinstance(value["objects"], list):
            raise ValueError("Invalid json format")

        geomap = GameLoader._load_map(value["map"])
        enemies: tp.Set[SupportsNpcProtocol] = set()

        for map_object_json in value["objects"]:
            world_object, coords = GameLoader._load_world_object(map_object_json)

            if isinstance(world_object, PlayerCharacter):
                player = world_object
            if isinstance(world_object, NPC):
                enemies.add(world_object)
            geomap.add_object(coords, world_object)

        return geomap, enemies, player
