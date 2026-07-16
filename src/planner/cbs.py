from __future__ import annotations
import heapq
from dataclasses import dataclass
from typing import List, Optional, Tuple
from .conflict import VertexConflict, find_earliest_conflict
from .grid import Grid
from .lowlevel_astar import astar_space_time
from .types import Agent, Constraints, EdgeConstraint, Path, VertexConstraint

def sum_of_costs(paths: List[Path]) -> int:
    return sum(max(0, len(p) - 1) for p in paths)

@dataclass(frozen=True)
class CTNode:
    cost: int
    tie: int
    constraints: Constraints
    paths: List[Path]

def _horizon(paths: List[Path]) -> int:
    return (max(len(p) for p in paths) if paths else 0) + 5

def cbs_solve(grid: Grid, agents: List[Agent], max_time: int) -> Optional[List[Path]]:
    root_constraints: Constraints = set()
    root_paths: List[Path] = []
    for i, a in enumerate(agents):
        p = astar_space_time(grid, a, i, root_constraints, max_time)
        if p is None:
            return None
        root_paths.append(p)

    root = CTNode(cost=sum_of_costs(root_paths), tie=0, constraints=root_constraints, paths=root_paths)
    open_heap: list[Tuple[int, int, CTNode]] = [(root.cost, root.tie, root)]
    heapq.heapify(open_heap)
    tie_counter = 1

    while open_heap:
        _, _, node = heapq.heappop(open_heap)
        conflict = find_earliest_conflict(node.paths, horizon=_horizon(node.paths))
        if conflict is None:
            return node.paths

        if isinstance(conflict, VertexConflict):
            for agent_idx in (conflict.a, conflict.b):
                new_constraints = set(node.constraints)
                new_constraints.add(VertexConstraint(agent=agent_idx, pos=conflict.pos, t=conflict.t))
                new_paths = list(node.paths)
                replanned = astar_space_time(grid, agents[agent_idx], agent_idx, new_constraints, max_time)
                if replanned is None:
                    continue
                new_paths[agent_idx] = replanned
                child = CTNode(cost=sum_of_costs(new_paths), tie=tie_counter, constraints=new_constraints, paths=new_paths)
                tie_counter += 1
                heapq.heappush(open_heap, (child.cost, child.tie, child))
        else:
            # Edge conflict
            for agent_idx, u, v in (
                (conflict.a, conflict.u_a, conflict.v_a),
                (conflict.b, conflict.u_b, conflict.v_b),
            ):
                new_constraints = set(node.constraints)
                new_constraints.add(EdgeConstraint(agent=agent_idx, u=u, v=v, t=conflict.t))
                new_paths = list(node.paths)
                replanned = astar_space_time(grid, agents[agent_idx], agent_idx, new_constraints, max_time)
                if replanned is None:
                    continue
                new_paths[agent_idx] = replanned
                child = CTNode(cost=sum_of_costs(new_paths), tie=tie_counter, constraints=new_constraints, paths=new_paths)
                tie_counter += 1
                heapq.heappush(open_heap, (child.cost, child.tie, child))

    return None
