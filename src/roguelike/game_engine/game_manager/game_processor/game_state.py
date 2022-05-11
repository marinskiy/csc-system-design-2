"""
Describes game state.
It stores all information about game: current view mode, environment, player and his inventory.
"""

from enum import Enum, auto

from roguelike.game_engine.env_manager import Environment, Inventory, map_objects_storage


class Key(Enum):
    W = "w"
    A = "a"
    S = "s"
    D = "d"
    E = "e"
    II = "i"
    M = "m"
    Q = "q"


class Mode(Enum):
    INVENTORY = auto()
    MAP = auto()


class GameState:
    """
    Stores all game parts

    Attributes:
        mode: current view mode
        environment: env with objects and map
        inventory: player's inventory
        player: main player
    """
    def __init__(
            self,
            mode: Mode,
            environment: Environment,
            inventory: Inventory,
            player: map_objects_storage.PlayerCharacter,
    ) -> None:
        self.mode = mode
        self.environment = environment
        self.inventory = inventory
        self.player = player
        self.is_running = True
