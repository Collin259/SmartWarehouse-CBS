from __future__ import annotations
from typing import Dict, List, Optional, Set, Tuple
from .grid import Grid
from .lowlevel_astar import astar_space_time
from .types import Agent, Constraints, EdgeConstraint, Path, Pos, VertexConstraint

class ReservationTable:
    def __init__(self) -> None:
        self.v: Dict[int, Set[Pos]] = {}
        self.e: Dict[int, Set[Tuple[Pos, Pos]]] = {}

    def reserve_path(self, path: Path, max_time: int) -> None:
        for t, p in enumerate(path):
            self.v.setdefault(t, set()).add(p)
        for t in range(len(path) - 1):
            self.e.setdefault(t, set()).add((path[t], path[t + 1]))
        g = path[-1]
        for t in range(len(path), max_time + 1):
            self.v.setdefault(t, set()).add(g)

    def as_constraints_for_agent(self, agent_index: int) -> Constraints:
        cons: Constraints = set()
        for t, ps in self.v.items():
            for p in ps:
                cons.add(VertexConstraint(agent=agent_index, pos=p, t=t))
        for t, es in self.e.items():
            for (u, v) in es:
                cons.add(EdgeConstraint(agent=agent_index, u=u, v=v, t=t))
                cons.add(EdgeConstraint(agent=agent_index, u=v, v=u, t=t))  # prevent swaps
        return cons

def independent_planning(grid: Grid, agents: List[Agent], max_time: int) -> Optional[List[Path]]:
    paths: List[Path] = []
    empty: Constraints = set()
    for i, a in enumerate(agents):
        p = astar_space_time(grid, a, i, empty, max_time)
        if p is None:
            return None
        paths.append(p)
    return paths

def prioritized_planning(grid: Grid, agents: List[Agent], max_time: int) -> Optional[List[Path]]:
    paths: List[Path] = []
    table = ReservationTable()
    for i, a in enumerate(agents):
        cons = table.as_constraints_for_agent(i)
        p = astar_space_time(grid, a, i, cons, max_time)
        if p is None:
            return None
        paths.append(p)
        table.reserve_path(p, max_time)
    return paths
