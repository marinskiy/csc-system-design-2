"""
Contains all classes to create character
"""
import json
import os
from roguelike.game_engine.env_manager.map_objects_storage import PlayerCharacter, Stats


class CharacterCreator:
    """Creates character with default stats"""

    @staticmethod
    def create() -> PlayerCharacter:
        character_file_path = os.path.join(os.path.dirname(__file__), "../../../../assets/default_character.json")
        with open(character_file_path, encoding="utf-8") as json_file:
            player_data = json.load(json_file)

        return PlayerCharacter(Stats(health=player_data["stats"]["health"], attack=player_data["stats"]["attack"]))
