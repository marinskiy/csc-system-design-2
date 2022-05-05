"""Contains high level classes for managing environment"""

import typing as tp
from dataclasses import dataclass

from PIL import Image

from roguelike import const
from roguelike.game_engine.env_manager.enemies import NPC
from roguelike.game_engine.env_manager.map import Map
from roguelike.ui.drawable import Drawable, load_image_resource
from roguelike.game_engine.env_manager.map_objects_storage import Treasure, MapObject, Stats


class InventoryPresenter(Drawable):
    """Class that governs the presentation of the Inventory"""

    def __init__(self, treasures: tp.Iterable[Treasure]) -> None:
        self._treasures = list(treasures)
        self._current = 0

    def add_treasure(self, treasure: Treasure) -> None:
        self._treasures.append(treasure)

    def select_next(self) -> None:
        if self._current + 1 < len(self._treasures):
            self._current += 1

    def select_previous(self) -> None:
        if self._current > 0:
            self._current -= 1

    def get_selected(self) -> tp.Optional[Treasure]:
        if self._treasures:
            return self._treasures[self._current]
        return None

    def _draw_inventory_cell(
            self,
            treasure_id: int,
            cell_size: int,
            mark_as_selected: bool,
    ) -> Image:
        storage = load_image_resource('empty_inventory.png', cell_size, cell_size).copy()
        if treasure_id >= len(self._treasures):
            return storage
        if not mark_as_selected:
            treasure = self._treasures[treasure_id].draw(cell_size, cell_size, draw_stats=True)
            storage.paste(treasure, (5, 5), treasure)
            return storage
        selection = load_image_resource('inventory_selection.png', cell_size, cell_size)
        storage.paste(selection, (0, 0), selection)
        treasure_icon = self._treasures[treasure_id].draw(cell_size - 10, cell_size - 10, draw_stats=True)
        storage.paste(treasure_icon, (5, 5), treasure_icon)
        return storage

    def draw(self, width: int, height: int) -> Image:
        assert width // const.INVENTORY_WIDTH == height // const.INVENTORY_HEIGHT
        assert width % const.INVENTORY_WIDTH == 0 and height % const.INVENTORY_HEIGHT == 0
        cell_size = width // const.INVENTORY_WIDTH
        result_image = Image.new('RGB', (width, height))
        current_treasure_id = 0
        for i in range(const.INVENTORY_WIDTH):
            for j in range(const.INVENTORY_HEIGHT):
                result_image.paste(
                    self._draw_inventory_cell(
                        current_treasure_id, cell_size=cell_size,
                        mark_as_selected=self._current == current_treasure_id),
                    (i * cell_size, j * cell_size))
                current_treasure_id += 1
        return result_image


class Inventory:
    """Class for describing player's inventory"""

    def __init__(self, treasures: tp.Iterable[Treasure]) -> None:
        self._treasure_is_worn = {treasure: False for treasure in treasures}
        self._presenter = InventoryPresenter(treasures)

    def get_additional_stats(self) -> Stats:
        return sum((treasure.stats
                    for treasure, is_on in self._treasure_is_worn.items()
                    if is_on), start=Stats(0, 0))

    def change_treasure_state(self, treasure: Treasure) -> None:
        self._treasure_is_worn[treasure] = not self._treasure_is_worn[treasure]

    def get_treasures(self) -> tp.Iterable[Treasure]:
        return tuple(self._treasure_is_worn)

    def add_treasure(self, treasure: Treasure) -> None:
        self._treasure_is_worn[treasure] = False
        self._presenter.add_treasure(treasure)

    @property
    def presenter(self) -> InventoryPresenter:
        return self._presenter


@dataclass
class Environment:
    map: Map
    enemies: tp.Set[NPC]
