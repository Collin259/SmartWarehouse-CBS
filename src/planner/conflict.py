from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple
from .types import Path, Pos

@dataclass(frozen=True)
class VertexConflict:
    a: int
    b: int
    pos: Pos
    t: int

@dataclass(frozen=True)
class EdgeConflict:
    a: int
    b: int
    u_a: Pos
    v_a: Pos
    u_b: Pos
    v_b: Pos
    t: int  # between t and t+1

Conflict = VertexConflict | EdgeConflict

def pos_at(path: Path, t: int) -> Pos:
    return path[t] if t < len(path) else path[-1]

def find_earliest_conflict(paths: List[Path], horizon: int) -> Optional[Conflict]:
    n = len(paths)
    for t in range(horizon):
        seen: dict[Pos, int] = {}
        for i in range(n):
            p = pos_at(paths[i], t)
            if p in seen:
                return VertexConflict(a=seen[p], b=i, pos=p, t=t)
            seen[p] = i

        if t + 1 < horizon:
            moves: dict[Tuple[Pos, Pos], int] = {}
            for i in range(n):
                u = pos_at(paths[i], t)
                v = pos_at(paths[i], t + 1)
                moves[(u, v)] = i
            for i in range(n):
                u = pos_at(paths[i], t)
                v = pos_at(paths[i], t + 1)
                j = moves.get((v, u))
                if j is not None and j != i:
                    a, b = (j, i) if j < i else (i, j)
                    return EdgeConflict(
                        a=a, b=b,
                        u_a=pos_at(paths[a], t), v_a=pos_at(paths[a], t + 1),
                        u_b=pos_at(paths[b], t), v_b=pos_at(paths[b], t + 1),
                        t=t
                    )
    return None
