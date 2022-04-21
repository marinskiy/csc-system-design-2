"""
Contains all classes run game loop
"""
from roguelike.game_engine.game_manager.action_processor.actions import ActionManager
from roguelike.game_engine.game_manager.game_processor.game_state import GameState, Key


class GameLoop:
    """Makes changes to game state according to player command"""
    def __init__(self, initial_state: GameState) -> None:
        self._state = initial_state
        self._action_manager = ActionManager()

    def run_game_turn(self, key: Key) -> GameState:
        self._action_manager.get_action(key, self._state)(self._state)
        return self._state
