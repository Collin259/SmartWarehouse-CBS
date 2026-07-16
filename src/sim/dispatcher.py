from __future__ import annotations
from typing import List, Tuple
from ..planner import Agent, Path
from .robot import RobotSim, MotionParams

def build_robots(agents: List[Agent], paths: List[Path], cell_center_fn, motion: MotionParams) -> List[RobotSim]:
    palette = [
        (52, 152, 219),
        (231, 76, 60),
        (46, 204, 113),
        (155, 89, 182),
        (241, 196, 15),
        (230, 126, 34),
        (26, 188, 156),
        (127, 140, 141),
    ]
    robots: List[RobotSim] = []
    for i, a in enumerate(agents):
        robots.append(RobotSim(
            name=a.name,
            color=palette[i % len(palette)],
            start_px=cell_center_fn(a.start),
            path_cells=paths[i],
            cell_center_fn=cell_center_fn,
            motion=motion,
        ))
    return robots
