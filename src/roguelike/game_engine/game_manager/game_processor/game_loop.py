"""
Contains all classes run game loop
"""
from ..action_processor.action_manager import ActionManager
from .game_state import GameState, Key


class GameLoop:
    """Makes changes to game state according to player command"""
    def __init__(self, initial_state: GameState) -> None:
        self._state = initial_state
        self._action_manager = ActionManager()

    def run_game_turn(self, key: Key) -> GameState:
        self._action_manager.get_action(key, self._state)(self._state)
        for enemy in self._state.environment.enemies:
            enemy.act(self._state.environment, self._state.player)
        return self._state
