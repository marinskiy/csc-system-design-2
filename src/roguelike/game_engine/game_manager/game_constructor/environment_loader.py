"""
Contains all classes needed to load game
"""

import typing as tp
from roguelike.game_engine.env_manager.map import MapCoordinates
from roguelike.game_engine.env_manager.map_objects_storage import Stats, Obstacle, Treasure, PlayerCharacter


def _load_coordinates(value: tp.List[int]) -> MapCoordinates:
    if len(value) != 2:
        raise ValueError("Invalid coordinates json")
    return MapCoordinates(value[0], value[1])


def _load_stats(value: tp.Dict[str, float]) -> Stats:
    if len(value) != 2 or "attack" not in value.keys() or "health" not in value.keys():
        raise ValueError("Invalid stats json")
    return Stats(value["health"], value["attack"])


def _load_obstacle(value: tp.Dict[str, tp.Any]) -> Obstacle:
    if len(value) != 0:
        raise ValueError("Invalid obstacle settings json")
    return Obstacle()


def _load_treasure(value: tp.Dict[str, tp.Any]) -> Treasure:
    if len(value) != 2 or "name" not in value.keys() or "stats" not in value.keys() or \
            not isinstance(value["name"], str):
        raise ValueError("Invalid treasure settings json")
    return Treasure(value["name"], _load_stats(value["stats"]))


def _load_player(value: tp.Dict[str, tp.Any]) -> PlayerCharacter:
    if len(value) != 1 or "stats" not in value.keys():
        raise ValueError("Invalid player settings json")
    return PlayerCharacter(_load_stats(value["stats"]))
