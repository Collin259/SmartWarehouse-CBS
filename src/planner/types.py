from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, List, Set, Union

Pos = Tuple[int, int]
Path = List[Pos]

@dataclass(frozen=True)
class Agent:
    name: str
    start: Pos
    goal: Pos

@dataclass(frozen=True)
class VertexConstraint:
    agent: int
    pos: Pos
    t: int

@dataclass(frozen=True)
class EdgeConstraint:
    agent: int
    u: Pos
    v: Pos
    t: int  # blocks movement u->v between t and t+1

Constraint = Union[VertexConstraint, EdgeConstraint]
Constraints = Set[Constraint]
