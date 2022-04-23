"""
Contains all classes needed to generate game
"""

import typing as tp
import random

from roguelike.game_engine.env_manager.map import Map
from roguelike.game_engine.game_manager.game_constructor.game_loader import check_dict_fields


class GameGenerator:
    """Generates GameState based on default settings"""

    @staticmethod
    def _get_random_value_from_range(value: tp.List[int]) -> int:
        if len(value) != 2 or value[0] > value[1]:
            raise ValueError("Invalid value range")
        return random.randint(value[0], value[1])

    @staticmethod
    def _decide_from_probability(value: float) -> bool:
        if value < 0 or value > 1:
            raise ValueError("Invalid probability")
        return random.random() < value

    @staticmethod
    def _generate_map(value: tp.Dict[str, tp.List[int]]) -> Map:
        if not check_dict_fields(value, ["width", "height"]):
            raise ValueError("Invalid map json")
        width = GameGenerator._get_random_value_from_range(value["width"])
        height = GameGenerator._get_random_value_from_range(value["height"])
        return Map(width, height)
