"""Implements algorithms for searching path between two points in a grid world"""
from __future__ import annotations

import heapq
import typing as tp

T = tp.TypeVar('T')
TPath = tp.Dict['Coordinates', 'Coordinates']


class Graph(tp.Protocol):
    def get_neighbours(
            self,
            coordinates: Coordinates,
    ) -> tp.Iterable[Coordinates]:
        pass


class Coordinates(tp.Protocol):
    x: int
    y: int


class PriorityQueue(tp.Generic[T]):
    """Standard priority queue"""

    def __init__(self) -> None:
        self.elements: tp.List[tp.Tuple[float, T]] = []

    def empty(self) -> bool:
        return not self.elements

    def put(self, item: T, priority: float) -> None:
        heapq.heappush(self.elements, (priority, item))

    def get(self) -> T:
        return heapq.heappop(self.elements)[1]


def eval_distance_using_heuristic(a: Coordinates, b: Coordinates) -> int:
    return abs(a.x - b.x) + abs(a.y - b.y)


def search_using_a_star(
        graph: Graph,
        start: Coordinates,
        destination: Coordinates,
) -> tp.Tuple[TPath, tp.Dict[Coordinates, int]]:
    frontier: PriorityQueue[Coordinates] = PriorityQueue()
    frontier.put(start, 0)
    came_from: TPath = {start: start}
    cost_so_far = {start: 0}

    while not frontier.empty():
        current = frontier.get()
        if current == destination:
            break
        for next_ in graph.get_neighbours(current):
            new_cost = cost_so_far[current] + 1
            is_first_visit = next_ not in cost_so_far
            if is_first_visit or new_cost < cost_so_far[next_]:
                cost_so_far[next_] = new_cost
                priority = new_cost + eval_distance_using_heuristic(next_, destination)
                frontier.put(next_, priority)
                came_from[next_] = current
    return came_from, cost_so_far
