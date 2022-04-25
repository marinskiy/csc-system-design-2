"""Contains Drawer"""

import typing as tp
from tempfile import NamedTemporaryFile

import PySimpleGUI as SimpleGUI
from PIL import Image

import roguelike.const as const


from roguelike.game_engine.env_manager.env_manager import Inventory
from roguelike.game_engine.env_manager.map_objects_storage import PlayerCharacter
from roguelike.game_engine.game_manager.game_processor.game_state import GameState


class Drawer:
    def __init__(self, map_width: int, map_height: int):
        self._map_width = map_width * const.MAP_TILE_SIZE
        self._map_height = map_height * const.MAP_TILE_SIZE
        self._inventory_width = const.INVENTORY_WIDTH * const.INVENTORY_TILE_SIZE
        self._inventory_height = const.INVENTORY_HEIGHT * const.INVENTORY_TILE_SIZE
        self._instantiate_window()
        self._map_id: tp.Optional[int] = None
        self._inventory_id: tp.Optional[int] = None
        self._player_info_id: tp.Optional[int] = None

    def draw(self, game_state: GameState) -> None:
        self._player_info_id = self._draw_player_info(
            game_state.player, game_state.inventory, self._player_info_id)
        self._map_id = self._draw_image(
            game_state.environment.map.draw(self._map_width, self._map_height), 0, 0, self._map_id)
        self._inventory_id = self._draw_image(
            game_state.inventory.presenter.draw(self._inventory_width, self._inventory_height),
            self._map_width, 0, self._inventory_id)

    def _instantiate_window(self) -> None:
        width = self._map_width + self._inventory_width
        height = max(self._map_height, self._inventory_height)
        layout = [
            [SimpleGUI.Button('Start')],
            [SimpleGUI.Text('World Map')],
            [SimpleGUI.Graph(
                canvas_size=(width, height), key='GRAPH',
                graph_bottom_left=(0, 0), graph_top_right=(width, height))],
        ]
        self._window = SimpleGUI.Window('Roguelike').Layout(layout)
        while True:
            event, _ = self._window.Read()
            if event == 'Start':
                break
        graph = self._window.Element('GRAPH')
        graph.draw_text(
            'Menu:\n'
            'w - up\n'
            'a - left\n'
            's - right\n'
            'd - down\n'
            'i - inventory mode\n'
            'm - play mode\n'
            'e - add item/equip item\n',
            location=(self._map_width + self._inventory_width // 2, self._map_height * 4 // 5))

    def _draw_image(
            self, img: Image, x_location: int, y_location: int, id_to_remove: tp.Optional[int]) -> int:
        graph = self._window.Element('GRAPH')
        if id_to_remove is not None:
            graph.delete_figure(id_to_remove)
        with NamedTemporaryFile(suffix='.png') as buff:
            img.save(buff, format='PNG')
            drawen_id = graph.draw_image(
                filename=buff.name, location=(x_location, y_location + img.size[1]))
            self._window.refresh()
        return drawen_id

    def _draw_player_info(
            self, player: PlayerCharacter, inventory: Inventory, id_to_remove: tp.Optional[int]) -> int:
        graph = self._window.Element('GRAPH')
        if id_to_remove is not None:
            graph.delete_figure(id_to_remove)
        stats = player.stats + inventory.get_additional_stats()
        return graph.draw_text(
            font=('bold', 15),
            text=f'Player: {stats.attack, stats.health}',
            location=(self._map_width + self._inventory_width // 2, self._inventory_height * 5 // 4))
