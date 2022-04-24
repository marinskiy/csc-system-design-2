"""Contains classes for managing mobs behaviour"""


class Behaviour:
    pass


class AggressiveBehaviour(Behaviour):
    pass


class CowardlyBehaviour(Behaviour):
    pass


class PassiveBehaviour(Behaviour):
    pass


class BehaviourFactory:
    """Produces behaviours of mobs"""

    def __init__(self) -> None:
        self._behaviours = {
            "aggressive": AggressiveBehaviour(),
            "cowardly": CowardlyBehaviour(),
            "passive": PassiveBehaviour()
        }

    def is_valid_key(self, key: str) -> bool:
        return key in self._behaviours

    def get_behaviour(self, key: str) -> Behaviour:
        return self._behaviours[key]
