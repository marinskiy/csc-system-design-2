"""
Contains all classes needed to load game
"""

import json
import typing as tp

from roguelike.game_engine.env_manager.env_manager import Environment, Inventory
from roguelike.game_engine.env_manager.map import MapCoordinates, Map
from roguelike.game_engine.env_manager.map_objects_storage import Stats, Obstacle, Treasure, PlayerCharacter, MapObject
from roguelike.game_engine.game_manager.game_processor.game_state import GameState, Mode


class GameLoader:
    """Loads GameState from file"""

    @staticmethod
    def load_game(path: str) -> GameState:
        with open(path, encoding="utf-8") as json_file:
            world_data = json.load(json_file)
        geomap, world_objects, player = GameLoader._load_world(world_data)
        return GameState(Mode.MAP, Environment(geomap, world_objects), Inventory([]), player)

    @staticmethod
    def _load_coordinates(value: tp.List[int]) -> MapCoordinates:
        if len(value) != 2:
            raise ValueError("Invalid coordinates json")
        return MapCoordinates(value[0], value[1])

    @staticmethod
    def _load_stats(value: tp.Dict[str, float]) -> Stats:
        if len(value) != 2 or "attack" not in value.keys() or "health" not in value.keys():
            raise ValueError("Invalid stats json")
        return Stats(value["health"], value["attack"])

    @staticmethod
    def _load_obstacle(value: tp.Dict[str, tp.Any]) -> Obstacle:
        if len(value) != 0:
            raise ValueError("Invalid obstacle settings json")
        return Obstacle()

    @staticmethod
    def _load_treasure(value: tp.Dict[str, tp.Any]) -> Treasure:
        if len(value) != 2 or "name" not in value.keys() or "stats" not in value.keys() or \
                not isinstance(value["name"], str):
            raise ValueError("Invalid treasure settings json")
        return Treasure(value["name"], GameLoader._load_stats(value["stats"]))

    @staticmethod
    def _load_player(value: tp.Dict[str, tp.Any]) -> PlayerCharacter:
        if len(value) != 1 or "stats" not in value.keys():
            raise ValueError("Invalid player settings json")
        return PlayerCharacter(GameLoader._load_stats(value["stats"]))

    @staticmethod
    def _load_map(value: tp.Dict[str, int]) -> Map:
        if len(value) != 2 or "width" not in value.keys() or "height" not in value.keys():
            raise ValueError("Invalid map json")
        return Map(value["width"], value["height"])

    @staticmethod
    def _load_world(value: tp.Dict[str, tp.Any]) -> tp.Tuple[Map, tp.List[tp.Any], PlayerCharacter]:
        if len(value) != 2 or "map" not in value.keys() or "objects" not in value.keys() or \
                not isinstance(value["objects"], list):
            raise ValueError("Invalid json format")

        geomap = GameLoader._load_map(value["map"])
        world_objects: tp.List[MapObject] = []

        for map_object_json in value["objects"]:
            if len(map_object_json) != 3 or "type" not in map_object_json.keys() \
                    or "pos" not in map_object_json.keys() or \
                    "settings" not in map_object_json.keys() or \
                    map_object_json["type"] not in ["player", "obstacle", "treasure"]:
                raise ValueError("Invalid map object json format")

            coords = GameLoader._load_coordinates(map_object_json["pos"])
            world_object: MapObject

            if map_object_json["type"] == "player":
                world_object = GameLoader._load_player(map_object_json["settings"])
            elif map_object_json["type"] == "obstacle":
                world_object = GameLoader._load_obstacle(map_object_json["settings"])
            elif map_object_json["type"] == "treasure":
                world_object = GameLoader._load_treasure(map_object_json["settings"])

            world_objects.append(world_object)
            if isinstance(world_object, PlayerCharacter):
                player = world_object
            geomap.add_object(coords, world_object)

        return geomap, world_objects, player
