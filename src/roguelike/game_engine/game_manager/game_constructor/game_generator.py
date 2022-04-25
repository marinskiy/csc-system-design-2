"""
Contains all classes needed to generate game
"""

import typing as tp
import random
import os
import json

from roguelike.game_engine.env_manager.enemies import Mob, BehaviourFactory
from roguelike.game_engine.env_manager.env_manager import Environment, Inventory
from roguelike.game_engine.env_manager.map import Map, MapCoordinates
from roguelike.game_engine.game_manager.game_constructor.game_loader import check_dict_fields
from roguelike.game_engine.env_manager.map_objects_storage import Stats, PlayerCharacter, Obstacle, Treasure, MapObject
from roguelike.game_engine.game_manager.game_processor.game_state import GameState, Mode


DEFAULT_GAME_SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "../../../../assets/default_game.json")
MOB_STATS_INCREASE_PER_LEVEL = 0.1


def get_random_int_from_range(value: tp.List[tp.Union[int]]) -> int:
    if len(value) != 2 or value[0] > value[1]:
        raise ValueError("Invalid value range")
    return random.randint(value[0], value[1])


class StatsGenerator:
    """Produces Stats based on settings"""

    def __init__(self, settings: tp.Dict[str, tp.List[int]]) -> None:
        self._validate_input(settings)
        self.health_range = settings["health"]
        self.attack_range = settings["attack"]

    @staticmethod
    def _validate_input(settings: tp.Dict[str, tp.List[int]]) -> None:
        if not check_dict_fields(settings, ["attack", "health"]):
            raise ValueError("Invalid stats settings json")

    def generate(self) -> Stats:
        health = get_random_int_from_range(self.health_range)
        attack = get_random_int_from_range(self.attack_range)
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

    @staticmethod
    def generate() -> Obstacle:
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


class MobGenerator:
    """Produces Mobs based on settings"""

    def __init__(self, settings: tp.Dict[str, tp.Any]) -> None:
        self.behaviour_factory = BehaviourFactory()
        self._validate_input(settings)
        self.level_range = settings["level"]
        self.radius_range = settings["radius"]
        self.behaviours_list = settings["behaviours"]
        self.stats_generator = StatsGenerator(settings["stats"])

    def _validate_input(self, settings: tp.Dict[str, tp.Any]) -> None:
        if not check_dict_fields(settings, ["level", "radius", "behaviours", "stats"]) or \
                not isinstance(settings["behaviours"], list):
            raise ValueError("Invalid mob settings json")

        for behaviour in settings["behaviours"]:
            if not isinstance(behaviour, str) or not self.behaviour_factory.is_valid_key(behaviour):
                raise ValueError("Invalid behaviour type")

    @staticmethod
    def _apply_level(stat: Stats, level: int) -> None:
        stat.health = int(stat.health * (1 + MOB_STATS_INCREASE_PER_LEVEL * level))
        stat.attack = int(stat.attack * (1 + MOB_STATS_INCREASE_PER_LEVEL * level))

    def generate(self) -> Mob:
        level = get_random_int_from_range(self.level_range)
        radius = get_random_int_from_range(self.radius_range)
        stats = self.stats_generator.generate()
        self._apply_level(stats, level)
        behaviour = self.behaviour_factory.get_behaviour(random.choice(self.behaviours_list))

        return Mob(level, stats, radius, behaviour)


class MapObjectGenerator:
    """Produces MapObject based on settings"""

    def __init__(self, settings: tp.Dict[str, tp.Any]) -> None:
        self._validate_input(settings)
        self.player_character_generator = PlayerCharacterGenerator(settings["player"])
        self.obstacle_generator = ObstacleGenerator(settings["obstacle"])
        self.treasure_generator = TreasureGenerator(settings["treasure"])
        self.mob_generator = MobGenerator(settings["mob"])

    @staticmethod
    def _validate_input(settings: tp.Dict[str, tp.Any]) -> None:
        if not check_dict_fields(settings, ["player", "obstacle", "treasure", "mob"]):
            raise ValueError("Invalid treasure settings json")

    def generate(self, key: str) -> MapObject:
        if key == "player":
            return self.player_character_generator.generate()
        elif key == "obstacle":
            return self.obstacle_generator.generate()
        elif key == "treasure":
            return self.treasure_generator.generate()
        elif key == "mob":
            return self.mob_generator.generate()
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
        width = get_random_int_from_range(self.width_range)
        height = get_random_int_from_range(self.height_range)
        return Map(width, height)

    @staticmethod
    def _validate_input(settings: tp.Dict[str, tp.List[int]]) -> None:
        if not check_dict_fields(settings, ["width", "height"]):
            raise ValueError("Invalid default map json")


class GameGenerator:
    """Generates GameState based on default settings"""

    def __init__(self) -> None:
        settings = self._load_settings()
        self.map_generator = MapGenerator(settings["map"])
        self.object_generator = MapObjectGenerator(settings["world_objects"])
        self.wheel = MapObjectWheel(settings["wheel"])

    @staticmethod
    def _validate_settings(settings: tp.Dict[str, tp.Any]) -> None:
        if not check_dict_fields(settings, ["map", "world_objects", "wheel"]):
            raise ValueError("Invalid default game json")

    def _load_settings(self) -> tp.Dict[str, tp.Any]:
        with open(DEFAULT_GAME_SETTINGS_FILE, encoding="utf-8") as json_file:
            settings = json.load(json_file)
        self._validate_settings(settings)
        return settings

    def generate(self) -> GameState:
        world_objects: tp.List[MapObject] = []
        geomap = self.map_generator.generate()

        player = self.object_generator.generate("player")
        if not isinstance(player, PlayerCharacter):
            raise ValueError("player should have type PlayerCharacter")
        world_objects.append(player)
        player_coordinates = MapCoordinates(get_random_int_from_range([0, geomap.get_width() - 1]),
                                            get_random_int_from_range([0, geomap.get_height() - 1]))
        geomap.add_object(player_coordinates, player)

        for i in range(geomap.get_width()):
            for j in range(geomap.get_height()):
                if len(geomap.get_objects(MapCoordinates(i, j))) == 0:
                    new_object_type = self.wheel.get_next_object_type()
                    if new_object_type == "none":
                        continue
                    new_object = self.object_generator.generate(new_object_type)
                    geomap.add_object(MapCoordinates(i, j), new_object)
                    world_objects.append(new_object)

        return GameState(Mode.MAP, Environment(geomap, world_objects, set()), Inventory([]), player)
