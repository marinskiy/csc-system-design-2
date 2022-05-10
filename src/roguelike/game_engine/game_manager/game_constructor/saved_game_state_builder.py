"""
Contains all classes needed to load game
"""

import json
import typing as tp

from roguelike.game_engine.env_manager import MapCoordinates, Map, Stats, MapObject
from roguelike.game_engine.env_manager.enemies import Mob, BehaviourFactory, ReplicatingMob
from roguelike.game_engine.env_manager.map_objects_storage import Obstacle, Treasure, PlayerCharacter
from roguelike.game_engine.game_manager.game_constructor.game_state_director import GameStateBuilder


def check_dict_fields(value: tp.Dict[str, tp.Any], names: tp.List[str]) -> bool:
    if len(value) != len(names):
        return False
    for name in names:
        if name not in value.keys():
            return False
    return True


def _validate_mob_settings_fields(value: tp.Dict[str, tp.Any]) -> bool:
    return isinstance(value["level"], int) and \
           isinstance(value["radius"], int) and \
           isinstance(value["behaviour"], str) and \
           BehaviourFactory.is_valid_key(value["behaviour"])


class SavedGameStateBuilder(GameStateBuilder):
    """Loads GameState from file"""

    def __init__(self) -> None:
        self._path = ""

    def set_path(self, path: str) -> "SavedGameStateBuilder":
        self._path = path
        return self

    def build(self) -> tp.Tuple[Map, tp.List[tp.Tuple[MapObject, MapCoordinates]]]:
        if not self._path:
            raise RuntimeError("You need to set map path before building game state with SavedGameStateBuilder")
        with open(self._path, encoding="utf-8") as json_file:
            world_data = json.load(json_file)
        return SavedGameStateBuilder._load_world(world_data)

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
        return Treasure(value["name"], SavedGameStateBuilder._load_stats(value["stats"]))

    @staticmethod
    def _load_mob(value: tp.Dict[str, tp.Any]) -> Mob:
        if not check_dict_fields(value, ["level", "radius", "behaviour", "stats"]) or \
                not _validate_mob_settings_fields(value):
            raise ValueError("Invalid mob settings json")

        return Mob(value["level"], SavedGameStateBuilder._load_stats(value["stats"]), value["radius"],
                   BehaviourFactory.get_behaviour(value["behaviour"]))

    @staticmethod
    def _load_replicating_mob(value: tp.Dict[str, tp.Any]) -> ReplicatingMob:
        if not check_dict_fields(value, ["level", "radius", "behaviour", "stats", "replication_rate",
                                         "replication_rate_decay"]) or \
                not _validate_mob_settings_fields(value) or \
                not isinstance(value["replication_rate"], float) or \
                not isinstance(value["replication_rate_decay"], float):
            raise ValueError("Invalid replicating mob settings json")

        return ReplicatingMob(value["level"], SavedGameStateBuilder._load_stats(value["stats"]), value["radius"],
                              BehaviourFactory.get_behaviour(value["behaviour"]), value["replication_rate"],
                              value["replication_rate_decay"])

    @staticmethod
    def _load_player(value: tp.Dict[str, tp.Any]) -> PlayerCharacter:
        if not check_dict_fields(value, ["stats"]):
            raise ValueError("Invalid player settings json")
        return PlayerCharacter(SavedGameStateBuilder._load_stats(value["stats"]))

    @staticmethod
    def _load_map(value: tp.Dict[str, int]) -> Map:
        if not check_dict_fields(value, ["width", "height"]):
            raise ValueError("Invalid map json")
        return Map(value["width"], value["height"])

    @staticmethod
    def _load_world_object(value: tp.Dict[str, tp.Any]) -> tp.Tuple[MapObject, MapCoordinates]:
        if not check_dict_fields(value, ["type", "pos", "settings"]) or \
                value["type"] not in ["player", "obstacle", "treasure", "mob", "replicating_mob"]:
            raise ValueError("Invalid map object json format")

        coords = SavedGameStateBuilder._load_coordinates(value["pos"])
        world_object: MapObject

        if value["type"] == "player":
            world_object = SavedGameStateBuilder._load_player(value["settings"])
        elif value["type"] == "obstacle":
            world_object = SavedGameStateBuilder._load_obstacle(value["settings"])
        elif value["type"] == "treasure":
            world_object = SavedGameStateBuilder._load_treasure(value["settings"])
        elif value["type"] == "mob":
            world_object = SavedGameStateBuilder._load_mob(value["settings"])
        elif value["type"] == "replicating_mob":
            world_object = SavedGameStateBuilder._load_replicating_mob(value["settings"])

        return world_object, coords

    @staticmethod
    def _load_world(value: tp.Dict[str, tp.Any]) -> tp.Tuple[Map, tp.List[tp.Tuple[MapObject, MapCoordinates]]]:
        if not check_dict_fields(value, ["map", "objects"]) or not isinstance(value["objects"], list):
            raise ValueError("Invalid json format")

        geomap = SavedGameStateBuilder._load_map(value["map"])
        world_objects_with_coords: tp.List[tp.Tuple[MapObject, MapCoordinates]] = []

        for map_object_json in value["objects"]:
            world_objects_with_coords.append(SavedGameStateBuilder._load_world_object(map_object_json))

        return geomap, world_objects_with_coords
