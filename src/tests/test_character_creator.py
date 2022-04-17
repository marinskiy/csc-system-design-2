"""Character creator tests"""

import json

from roguelike.game_engine.game_manager.game_constructor.character_creator import CharacterCreator


def test_default_character() -> None:
    player = CharacterCreator.create()
    with open('../assets/default_character.json') as json_file:
        player_data = json.load(json_file)

    assert player.stats.attack == player_data["stats"]["attack"]
    assert player.stats.health == player_data["stats"]["health"]
