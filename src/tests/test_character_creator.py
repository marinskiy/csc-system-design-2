"""Character creator tests"""

import json
import os

from roguelike.game_engine.game_manager.game_constructor.character_creator import CharacterCreator


def test_default_character() -> None:
    player = CharacterCreator.create()
    character_file_path = os.path.join(os.path.dirname(__file__), "../assets/default_character.json")
    with open(character_file_path, encoding="utf-8") as json_file:
        player_data = json.load(json_file)

    assert player.stats.attack == player_data["stats"]["attack"]
    assert player.stats.health == player_data["stats"]["health"]
