from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional
import math
from ..planner import Path

@dataclass
class MotionParams:
    move_time_s: float = 1.0
    wait_time_s: float = 1.0
    arrive_eps_px: float = 2.0

class RobotSim:
    def __init__(self, name: str, color: Tuple[int,int,int], start_px: Tuple[float,float], path_cells: Path, cell_center_fn, motion: MotionParams):
        self.name = name
        self.color = color
        self.motion = motion
        self.cell_center_fn = cell_center_fn
        self.path_cells = path_cells
        self.i = 0
        self.pos = [start_px[0], start_px[1]]
        self.heading = 0.0
        self.state = "MOVING"
        self._wait_left = 0.0

        # segment tracking for constant speed
        self._seg_to: Optional[Tuple[float,float]] = None
        self._seg_len: float = 0.0

    def _target_px(self) -> Optional[Tuple[float,float]]:
        if self.i >= len(self.path_cells) - 1:
            return None
        return self.cell_center_fn(self.path_cells[self.i + 1])

    def _start_segment_if_needed(self, tx: float, ty: float):
        if self._seg_to != (tx, ty):
            self._seg_to = (tx, ty)
            self._seg_len = math.hypot(tx - self.pos[0], ty - self.pos[1])

    def update(self, dt: float):
        if self.state == "DONE":
            return
        if self.i >= len(self.path_cells) - 1:
            self.state = "DONE"
            return

        cur_cell = self.path_cells[self.i]
        nxt_cell = self.path_cells[self.i + 1]

        # WAIT step
        if nxt_cell == cur_cell:
            if self._wait_left <= 0.0:
                self._wait_left = self.motion.wait_time_s
                self.state = "WAITING"
            self._wait_left -= dt
            if self._wait_left <= 0.0:
                self.i += 1
                self.state = "MOVING"
            return

        tx, ty = self._target_px()
        dx = tx - self.pos[0]
        dy = ty - self.pos[1]
        dist = math.hypot(dx, dy)

        if dist <= self.motion.arrive_eps_px:
            self.pos[0], self.pos[1] = tx, ty
            self.i += 1
            self.state = "MOVING"
            self._seg_to = None
            return

        self._start_segment_if_needed(tx, ty)
        seg_len = max(1e-6, self._seg_len)
        speed = seg_len / max(1e-6, self.motion.move_time_s)
        step = speed * dt

        if step >= dist:
            self.pos[0], self.pos[1] = tx, ty
            self.i += 1
            self._seg_to = None
        else:
            ux = dx / dist
            uy = dy / dist
            self.pos[0] += ux * step
            self.pos[1] += uy * step

        # smooth heading
        desired = math.atan2(dy, dx)
        diff = (desired - self.heading + math.pi) % (2*math.pi) - math.pi
        self.heading += diff * min(1.0, 6.0 * dt)
