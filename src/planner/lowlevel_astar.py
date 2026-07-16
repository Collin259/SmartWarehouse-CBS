from __future__ import annotations
import heapq
from typing import Dict, Optional, Set, Tuple
from .grid import Grid
from .types import Agent, Constraints, EdgeConstraint, Path, Pos, VertexConstraint

State = Tuple[Pos, int]  # (position, time)

def manhattan(a: Pos, b: Pos) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def _build_constraint_lookup(agent_index: int, constraints: Constraints):
    v_block: Dict[int, Set[Pos]] = {}
    e_block: Dict[int, Set[Tuple[Pos, Pos]]] = {}
    for c in constraints:
        if isinstance(c, VertexConstraint) and c.agent == agent_index:
            v_block.setdefault(c.t, set()).add(c.pos)
        elif isinstance(c, EdgeConstraint) and c.agent == agent_index:
            e_block.setdefault(c.t, set()).add((c.u, c.v))
    return v_block, e_block

def astar_space_time(grid: Grid, agent: Agent, agent_index: int, constraints: Constraints, max_time: int) -> Optional[Path]:
    '''
    Space-time A* for a single agent with constraints.
    State: (pos, t). Actions: move 4-neighbor or WAIT. Each action costs 1.
    '''
    v_block, e_block = _build_constraint_lookup(agent_index, constraints)

    start: State = (agent.start, 0)
    if 0 in v_block and agent.start in v_block[0]:
        return None

    open_heap: list[tuple[int, int, Pos, int]] = []
    heapq.heappush(open_heap, (manhattan(agent.start, agent.goal), 0, agent.start, 0))

    came_from: Dict[State, State] = {}
    g_score: Dict[State, int] = {start: 0}

    def is_vertex_blocked(p: Pos, t: int) -> bool:
        s = v_block.get(t)
        return (s is not None) and (p in s)

    def is_edge_blocked(u: Pos, v: Pos, t: int) -> bool:
        s = e_block.get(t)
        return (s is not None) and ((u, v) in s)

    while open_heap:
        f, g, pos, t = heapq.heappop(open_heap)
        state: State = (pos, t)
        if g != g_score.get(state, 10**18):
            continue

        if pos == agent.goal:
            path_rev: list[Pos] = [pos]
            cur = state
            while cur in came_from:
                cur = came_from[cur]
                path_rev.append(cur[0])
            path_rev.reverse()
            return path_rev

        if t >= max_time:
            continue

        next_t = t + 1
        candidates = [pos, *grid.neighbors4(pos)]  # WAIT + moves
        for nxt in candidates:
            if not grid.in_bounds(nxt) or not grid.passable(nxt):
                continue
            if is_vertex_blocked(nxt, next_t):
                continue
            if is_edge_blocked(pos, nxt, t):
                continue

            nxt_state: State = (nxt, next_t)
            tentative_g = g + 1
            if tentative_g < g_score.get(nxt_state, 10**18):
                came_from[nxt_state] = state
                g_score[nxt_state] = tentative_g
                h = manhattan(nxt, agent.goal)
                heapq.heappush(open_heap, (tentative_g + h, tentative_g, nxt, next_t))

    return None
