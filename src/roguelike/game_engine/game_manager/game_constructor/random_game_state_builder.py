# mypy: ignore-errors
"""
Contains all classes needed to generate game
"""
import itertools
import json
import os
import random
import typing as tp

from roguelike.game_engine.env_manager.enemies import \
    MobStyle, Mob, Ghost, OneHitGuy, BehaviourFactory, Behaviour, ReplicatingMob
from roguelike.game_engine.env_manager.map import Map, MapCoordinates
from roguelike.game_engine.env_manager.map_objects_storage import Stats, PlayerCharacter, Obstacle, Treasure, \
    MapObject
from roguelike.game_engine.game_manager.game_constructor.game_state_director import GameStateBuilder
from roguelike.game_engine.game_manager.game_constructor.saved_game_state_builder import check_dict_fields

DEFAULT_GAME_SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "../../../../assets/default_game.json")
MOB_STATS_INCREASE_PER_LEVEL = 0.1


def get_random_int_from_range(value: tp.List[int]) -> int:
    if len(value) != 2 or value[0] > value[1]:
        raise ValueError("Invalid value range")
    return random.randint(value[0], value[1])


def get_random_float_from_range(value: tp.List[float]) -> float:
    if len(value) != 2 or value[0] > value[1]:
        raise ValueError("Invalid value range")
    return random.uniform(value[0], value[1])


class StatsBuilder:
    """Produces Stats based on settings"""

    def __init__(self, settings: tp.Dict[str, tp.List[int]]) -> None:
        self._validate_input(settings)
        self.health_range = settings["health"]
        self.attack_range = settings["attack"]

    @staticmethod
    def _validate_input(settings: tp.Dict[str, tp.List[int]]) -> None:
        if not check_dict_fields(settings, ["attack", "health"]):
            raise ValueError("Invalid stats settings json")

    def build(self) -> Stats:
        health = get_random_int_from_range(self.health_range)
        attack = get_random_int_from_range(self.attack_range)
        return Stats(health, attack)


class PlayerCharacterBuilder:
    """Produces PlayerCharacter based on settings"""

    def __init__(self, settings: tp.Dict[str, tp.Any]) -> None:
        self._validate_input(settings)
        self.stats_generator = StatsBuilder(settings["stats"])

    @staticmethod
    def _validate_input(settings: tp.Dict[str, tp.Any]) -> None:
        if not check_dict_fields(settings, ["stats"]):
            raise ValueError("Invalid player settings json")

    def build(self) -> PlayerCharacter:
        return PlayerCharacter(self.stats_generator.build())


class ObstacleBuilder:
    """Produces Obstacle based on settings"""

    def __init__(self, settings: tp.Dict[str, tp.Any]) -> None:
        self._validate_input(settings)

    @staticmethod
    def _validate_input(settings: tp.Dict[str, tp.Any]) -> None:
        if len(settings) != 0:
            raise ValueError("Invalid obstacle settings json")

    @staticmethod
    def build() -> Obstacle:
        return Obstacle()


class TreasureBuilder:
    """Produces Treasure based on settings"""

    def __init__(self, settings: tp.Dict[str, tp.Any]) -> None:
        self._validate_input(settings)
        self.names_list = settings["names"]
        self.stats_generator = StatsBuilder(settings["stats"])

    @staticmethod
    def _validate_input(settings: tp.Dict[str, tp.Any]) -> None:
        if not check_dict_fields(settings, ["names", "stats"]) or not isinstance(settings["names"], list):
            raise ValueError("Invalid treasure settings json")

    def build(self) -> Treasure:
        return Treasure(random.choice(self.names_list), self.stats_generator.build())


class AbstractMobFactory:
    """Abstract factory for generating mobs"""

    DRAW_FLAVOUR = None

    @classmethod
    def get_mob(cls, style, *args) -> Mob:   # type: ignore
        if style == MobStyle.GHOST:
            return Ghost(*args, draw_flavour=cls.DRAW_FLAVOUR)  # pylint: disable=E1123
        elif style == MobStyle.ONE_HIT_GUY:
            return OneHitGuy(*args, draw_flavour=cls.DRAW_FLAVOUR)  # pylint: disable=E1123
        else:
            return Mob(*args, draw_flavour=cls.DRAW_FLAVOUR)  # pylint: disable=E1123


class DefaultMobFactory(AbstractMobFactory):
    """Factory for generating default mobs"""

    DRAW_FLAVOUR = "default"


class DotaMobFactory(AbstractMobFactory):
    """Factory for generating dota mobs"""

    DRAW_FLAVOUR = "dota"


class MobBuilder:
    """Produces Mobs based on settings"""

    def __init__(self, settings: tp.Dict[str, tp.Any]) -> None:
        self._validate_input(settings)
        self.level_range = settings["level"]
        self.radius_range = settings["radius"]
        self.behaviours_list = settings["behaviours"]
        self.stats_generator = StatsBuilder(settings["stats"])
        self.style_indicators = settings["style_indicators"]
        self._mob_factory = DotaMobFactory() if os.environ.get("DOTA_ENV") else DefaultMobFactory()

    def _validate_input(self, settings: tp.Dict[str, tp.Any]) -> None:
        if not check_dict_fields(settings, ["style_indicators", "level", "radius", "behaviours", "stats"]) or \
                not isinstance(settings["behaviours"], list):
            raise ValueError("Invalid mob settings json")

        for behaviour in settings["behaviours"]:
            if not isinstance(behaviour, str) or not BehaviourFactory.is_valid_key(behaviour):
                raise ValueError("Invalid behaviour type")

    @staticmethod
    def _apply_level(stat: Stats, level: int) -> None:
        stat.health = int(stat.health * (1 + MOB_STATS_INCREASE_PER_LEVEL * level))
        stat.attack = int(stat.attack * (1 + MOB_STATS_INCREASE_PER_LEVEL * level))

    def generate_parameters(self) -> tp.Tuple[int, Stats, int, Behaviour]:
        level = get_random_int_from_range(self.level_range)
        radius = get_random_int_from_range(self.radius_range)
        stats = self.stats_generator.build()
        self._apply_level(stats, level)
        behaviour = BehaviourFactory.get_behaviour(random.choice(self.behaviours_list))

        return level, stats, radius, behaviour

    def build(self) -> Mob:
        style_ind = get_random_int_from_range([0, self.style_indicators["total"]])
        style = MobStyle.NORMAL
        for style_name, border in self.style_indicators["range"].items():
            if border <= style_ind:
                style = MobStyle(style_name)
                break
        return self._mob_factory.get_mob(style, *self.generate_parameters())


class ReplicatingMobBuilder:
    """Produces replicating mobs based on settings and MobGenerator"""

    def __init__(self, mob_generator: MobBuilder, settings: tp.Dict[str, tp.Any]) -> None:
        self._validate_input(settings)
        self.mob_builder = mob_generator
        self.replication_rate_range = settings["replication_rate"]
        self.replication_rate_decay_range = settings["replication_rate_decay"]

    @staticmethod
    def _validate_input(settings: tp.Dict[str, tp.Any]) -> None:
        if not check_dict_fields(settings, ["replication_rate", "replication_rate_decay"]):
            raise ValueError("Invalid replication mob settings json")

    def build(self) -> ReplicatingMob:
        replication_rate = get_random_float_from_range(self.replication_rate_range)
        replication_rate_decay = get_random_float_from_range(self.replication_rate_decay_range)
        level, stats, radius, behaviour = self.mob_builder.generate_parameters()
        flavour = "default" if os.environ.get("DOTA_ENV") else "default"
        return ReplicatingMob(  # pylint: disable=E1123
            level, stats, radius, behaviour,
            replication_rate, replication_rate_decay, draw_flavour=flavour)


class MapObjectBuilder:
    """Produces MapObject based on settings"""

    def __init__(self, settings: tp.Dict[str, tp.Any]) -> None:
        self._validate_input(settings)
        self.player_character_builder = PlayerCharacterBuilder(settings["player"])
        self.obstacle_builder = ObstacleBuilder(settings["obstacle"])
        self.treasure_builder = TreasureBuilder(settings["treasure"])
        self.mob_builder = MobBuilder(settings["mob"])
        self.replicating_mob_builder = ReplicatingMobBuilder(self.mob_builder, settings["replicating_mob"])

    @staticmethod
    def _validate_input(settings: tp.Dict[str, tp.Any]) -> None:
        if not check_dict_fields(settings, ["player", "obstacle", "treasure", "mob", "replicating_mob"]):
            raise ValueError("Invalid world_objects settings json")

    def build(self, key: str) -> MapObject:
        if key == "player":
            return self.player_character_builder.build()
        elif key == "obstacle":
            return self.obstacle_builder.build()
        elif key == "treasure":
            return self.treasure_builder.build()
        elif key == "mob":
            return self.mob_builder.build()
        elif key == "replicating_mob":
            return self.replicating_mob_builder.build()
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


class MapBuilder:
    """Produces Map based on settings"""

    def __init__(self, settings: tp.Dict[str, tp.List[int]]) -> None:
        self._validate_input(settings)
        self.width_range = settings["width"]
        self.height_range = settings["height"]
        self.width: tp.Optional[int] = None
        self.height: tp.Optional[int] = None

    def set_dimensions(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    def build(self) -> Map:
        if self.width is None or self.height is None:
            self.width = get_random_int_from_range(self.width_range)
            self.height = get_random_int_from_range(self.height_range)
        return Map(self.width, self.height)

    @staticmethod
    def _validate_input(settings: tp.Dict[str, tp.List[int]]) -> None:
        if not check_dict_fields(settings, ["width", "height"]):
            raise ValueError("Invalid default map json")


class RandomGameStateBuilder(GameStateBuilder):
    """Generates GameState based on default settings"""

    def __init__(self) -> None:
        settings = self._load_settings()
        self.map_builder = MapBuilder(settings["map"])
        self.object_builder = MapObjectBuilder(settings["world_objects"])
        self.wheel = MapObjectWheel(settings["wheel"])

    def set_map_dimensions(self, width: int, height: int) -> "RandomGameStateBuilder":
        self.map_builder.set_dimensions(width, height)
        return self

    def build(self) -> tp.Tuple[Map, tp.List[tp.Tuple[MapObject, MapCoordinates]]]:
        geomap = self.map_builder.build()
        world_objects_with_coords: tp.List[tp.Tuple[MapObject, MapCoordinates]] = []

        player = self.object_builder.build("player")
        if not isinstance(player, PlayerCharacter):
            raise ValueError("player should have type PlayerCharacter")
        player_coordinates = MapCoordinates(get_random_int_from_range([0, geomap.get_width() - 1]),
                                            get_random_int_from_range([0, geomap.get_height() - 1]))
        world_objects_with_coords.append((player, player_coordinates))

        for i, j in itertools.product(range(geomap.get_width()),
                                      range(geomap.get_height())):
            new_coords = MapCoordinates(i, j)
            if player_coordinates == new_coords:
                continue

            new_object_type = self.wheel.get_next_object_type()
            if new_object_type == "none":
                continue

            new_object = self.object_builder.build(new_object_type)
            world_objects_with_coords.append((new_object, new_coords))

        return geomap, world_objects_with_coords

    @staticmethod
    def _validate_settings(settings: tp.Dict[str, tp.Any]) -> None:
        if not check_dict_fields(settings, ["map", "world_objects", "wheel"]):
            raise ValueError("Invalid default game json")

    def _load_settings(self) -> tp.Dict[str, tp.Any]:
        with open(DEFAULT_GAME_SETTINGS_FILE, encoding="utf-8") as json_file:
            settings = json.load(json_file)
        self._validate_settings(settings)
        return settings
