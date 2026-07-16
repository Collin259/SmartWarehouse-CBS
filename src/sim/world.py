from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple
from ..planner import Grid

@dataclass(frozen=True)
class RenderConfig:
    cell_px: int = 48
    margin_px: int = 16
    sidebar_px: int = 260

class World:
    def __init__(self, grid: Grid, cfg: RenderConfig):
        self.grid = grid
        self.cfg = cfg

    def grid_to_px_center(self, cell: Tuple[int,int]) -> Tuple[float, float]:
        x, y = cell
        cx = self.cfg.margin_px + x * self.cfg.cell_px + self.cfg.cell_px / 2
        cy = self.cfg.margin_px + y * self.cfg.cell_px + self.cfg.cell_px / 2
        return (cx, cy)

    def size_px(self) -> Tuple[int,int]:
        w = self.cfg.margin_px * 2 + self.grid.w * self.cfg.cell_px + self.cfg.sidebar_px
        h = self.cfg.margin_px * 2 + self.grid.h * self.cfg.cell_px
        return (w, h)

    def cell_rect_px(self, cell: Tuple[int,int]) -> Tuple[int,int,int,int]:
        x,y = cell
        left = self.cfg.margin_px + x * self.cfg.cell_px
        top  = self.cfg.margin_px + y * self.cfg.cell_px
        return (left, top, self.cfg.cell_px, self.cfg.cell_px)
