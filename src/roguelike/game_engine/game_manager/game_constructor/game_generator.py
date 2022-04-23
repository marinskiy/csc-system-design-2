"""
Contains all classes needed to generate game
"""

import typing as tp
import random

from roguelike.game_engine.env_manager.map import Map
from roguelike.game_engine.game_manager.game_constructor.game_loader import check_dict_fields
from roguelike.game_engine.env_manager.map_objects_storage import Stats, PlayerCharacter, Obstacle, Treasure, MapObject


def get_random_value_from_range(value: tp.List[tp.Union[int, float]]) -> int:
    if len(value) != 2 or value[0] > value[1]:
        raise ValueError("Invalid value range")

    if isinstance(value[0], int):
        return random.randint(value[0], value[1])
    return random.uniform(value[0], value[1])


class StatsGenerator:
    """Produces Stats based on settings"""

    def __init__(self, settings: tp.Dict[str, tp.List[float]]) -> None:
        self._validate_input(settings)
        self.health_range = settings["health"]
        self.attack_range = settings["attack"]

    @staticmethod
    def _validate_input(settings: tp.Dict[str, tp.List[float]]) -> None:
        if not check_dict_fields(settings, ["attack", "health"]):
            raise ValueError("Invalid stats settings json")

    def generate(self) -> Stats:
        health = get_random_value_from_range(self.health_range)
        attack = get_random_value_from_range(self.attack_range)
        return Stats(health, attack)


class PlayerCharacterGenerator:
    """Produces PlayerCharacter based on settings"""

    def __init__(self, settings: tp.Dict[str, tp.Any]) -> None:
        self._validate_input(settings)
        self.stats_generator = StatsGenerator(settings["stats"])

    @staticmethod
    def _validate_input(settings: tp.Dict[str, tp.Any]) -> None:
        if not check_dict_fields(settings, ["stats"]):
            raise ValueError("Invalid player settings json")

    def generate(self) -> PlayerCharacter:
        return PlayerCharacter(self.stats_generator.generate())


class ObstacleGenerator:
    """Produces Obstacle based on settings"""

    def __init__(self, settings: tp.Dict[str, tp.Any]) -> None:
        self._validate_input(settings)

    @staticmethod
    def _validate_input(settings: tp.Dict[str, tp.Any]) -> None:
        if len(settings) != 0:
            raise ValueError("Invalid obstacle settings json")

    def generate(self) -> Obstacle:
        return Obstacle()


class TreasureGenerator:
    """Produces Treasure based on settings"""

    def __init__(self, settings: tp.Dict[str, tp.Any]) -> None:
        self._validate_input(settings)
        self.names_list = settings["names"]
        self.stats_generator = StatsGenerator(settings["stats"])

    @staticmethod
    def _validate_input(settings: tp.Dict[str, tp.Any]) -> None:
        if not check_dict_fields(settings, ["names", "stats"]) or not isinstance(settings["names"], list):
            raise ValueError("Invalid treasure settings json")

    def generate(self) -> Treasure:
        return Treasure(random.choice(self.names_list), self.stats_generator.generate())


class MapObjectGenerator:
    """Produces MapObject based on settings"""

    def __init__(self, settings: tp.Dict[str, tp.Any]) -> None:
        self._validate_input(settings)
        self.player_character_generator = PlayerCharacterGenerator(settings["player"])
        self.obstacle_generator = ObstacleGenerator(settings["obstacle"])
        self.treasure_generator = TreasureGenerator(settings["treasure"])

    @staticmethod
    def _validate_input(settings: tp.Dict[str, tp.Any]) -> None:
        if not check_dict_fields(settings, ["player", "obstacle", "treasure"]):
            raise ValueError("Invalid treasure settings json")

    def generate(self, key: str) -> MapObject:
        if key == "player":
            return self.player_character_generator.generate()
        elif key == "obstacle":
            return self.obstacle_generator.generate()
        elif key == "treasure":
            return self.treasure_generator.generate()
        else:
            raise ValueError("No such MapObject")


class MapObjectWheel:
    """Chooses map object based on weights"""

    def __init__(self, settings: tp.Dict[str, tp.List[tp.Any]]) -> None:
        self._validate_input(settings)
        self.population = settings["population"]
        self.weights = settings["weights"]

    def get_next_object_type(self) -> str:
        return random.choices(self.population, self.weights)[0]

    @staticmethod
    def _validate_input(settings: tp.Dict[str, tp.List[tp.Any]]) -> None:
        if not check_dict_fields(settings, ["population", "weights"]) or len(
                settings["population"]) == 0 or len(settings["population"]) != len(settings["weights"]):
            raise ValueError("Invalid wheel settings json")


class MapGenerator:
    """Produces Map based on settings"""

    def __init__(self, settings: tp.Dict[str, tp.List[int]]) -> None:
        self._validate_input(settings)
        self.width_range = settings["width"]
        self.height_range = settings["height"]

    def generate(self) -> Map:
        width = get_random_value_from_range(self.width_range)
        height = get_random_value_from_range(self.height_range)
        return Map(width, height)

    @staticmethod
    def _validate_input(settings: tp.Dict[str, tp.List[int]]) -> None:
        if not check_dict_fields(settings, ["width", "height"]):
            raise ValueError("Invalid default map json")


class GameGenerator:
    """Generates GameState based on default settings"""

