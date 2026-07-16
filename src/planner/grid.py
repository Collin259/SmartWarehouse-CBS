from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Set
from .types import Pos

@dataclass(frozen=True)
class Grid:
    w: int
    h: int
    obstacles: Set[Pos]

    def in_bounds(self, p: Pos) -> bool:
        x, y = p
        return 0 <= x < self.w and 0 <= y < self.h

    def passable(self, p: Pos) -> bool:
        return p not in self.obstacles

    def neighbors4(self, p: Pos) -> Iterable[Pos]:
        x, y = p
        for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if self.in_bounds(q) and self.passable(q):
                yield q
