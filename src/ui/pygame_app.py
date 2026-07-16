from __future__ import annotations
import json, time
from dataclasses import dataclass
from typing import List
import pygame

from ..planner import Agent, Grid, independent_planning, prioritized_planning, cbs_solve
from ..sim.world import World, RenderConfig
from ..sim.dispatcher import build_robots
from ..sim.robot import MotionParams
from .draw import draw_world, draw_goals, draw_paths, draw_robots, draw_sidebar

@dataclass
class Scenario:
    name: str
    grid: Grid
    agents: List[Agent]
    max_time: int

def load_scenario(path: str) -> Scenario:
    with open(path, "r", encoding="utf-8") as f:
        s = json.load(f)
    grid = Grid(w=s["grid"]["width"], h=s["grid"]["height"], obstacles=set(tuple(o) for o in s.get("obstacles", [])))
    agents = [Agent(a["id"], tuple(a["start"]), tuple(a["goal"])) for a in s["agents"]]
    return Scenario(name=s.get("name", path), grid=grid, agents=agents, max_time=int(s.get("max_time", 200)))

def plan(algo: str, sc: Scenario):
    if algo == "independent":
        return independent_planning(sc.grid, sc.agents, sc.max_time)
    if algo == "prioritized":
        return prioritized_planning(sc.grid, sc.agents, sc.max_time)
    if algo == "cbs":
        return cbs_solve(sc.grid, sc.agents, sc.max_time)
    raise ValueError(algo)

class App:
    def __init__(self, scenario_path: str, algo: str):
        pygame.init()
        pygame.display.set_caption("CBS MAPF — Smooth Motion Simulator (pygame)")
        self.cfg = RenderConfig()
        self.motion = MotionParams(move_time_s=1.0, wait_time_s=1.0)

        self.scenario_paths = {
            "1": "scenarios/demo_01_corridor.json",
            "2": "scenarios/demo_02_intersection.json",
            "3": "scenarios/demo_03_bottleneck.json",
        }

        self.algo = algo
        self.sc = load_scenario(scenario_path)
        self.world = World(self.sc.grid, self.cfg)
        self.screen = pygame.display.set_mode(self.world.size_px())
        self.clock = pygame.time.Clock()

        self.running = False
        self.speed = 1.0
        self.show_paths = True

        self.paths = None
        self.robots = []
        self.sim_time = 0.0
        self.last_plan_runtime = 0.0
        self.replan()

    def replan(self):
        # feedback so harder scenarios don't feel frozen
        self.screen.fill((255,255,255))
        font = pygame.font.SysFont(None, 28)
        msg = font.render('Planning...', True, (0,0,0))
        self.screen.blit(msg, (20, 20))
        pygame.display.flip()
        t0 = time.perf_counter()
        self.paths = plan(self.algo, self.sc)
        self.last_plan_runtime = time.perf_counter() - t0
        if self.paths is None:
            raise RuntimeError("No solution found for this scenario/algo.")
        self.world = World(self.sc.grid, self.cfg)
        self.screen = pygame.display.set_mode(self.world.size_px())
        self.robots = build_robots(self.sc.agents, self.paths, self.world.grid_to_px_center, self.motion)
        self.sim_time = 0.0

    def reset_time(self):
        self.robots = build_robots(self.sc.agents, self.paths, self.world.grid_to_px_center, self.motion)
        self.sim_time = 0.0

    def set_algo(self, algo: str):
        self.algo = algo
        self.replan()

    def set_scenario(self, key: str):
        self.sc = load_scenario(self.scenario_paths[key])
        self.replan()

    def update(self, dt: float):
        if not self.running:
            return
        dt *= self.speed
        self.sim_time += dt
        for r in self.robots:
            r.update(dt)

    def draw(self):
        draw_world(self.screen, self.world, self.sc.grid)
        draw_goals(self.screen, self.world, self.sc.agents)
        if self.show_paths and self.paths is not None:
            draw_paths(self.screen, self.world, self.paths)
        draw_robots(self.screen, self.robots)

        info = [
            f"Scenario: {self.sc.name}",
            f"Plan time: {self.last_plan_runtime*1000:.1f} ms",
            f"Robots: {len(self.sc.agents)}",
            f"Move time: {self.motion.move_time_s:.1f}s/cell",
        ]
        draw_sidebar(self.screen, self.world, "CBS Routing Demo", self.algo, self.running, self.speed, self.sim_time, info)
        pygame.display.flip()

    def loop(self):
        while True:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); return
                    if event.key == pygame.K_SPACE:
                        self.running = not self.running
                    if event.key == pygame.K_o:
                        self.show_paths = not self.show_paths
                    if event.key == pygame.K_r:
                        self.reset_time()
                    if event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                        self.speed = min(8.0, self.speed * 1.25)
                    if event.key == pygame.K_MINUS:
                        self.speed = max(0.25, self.speed / 1.25)
                    if event.key == pygame.K_i:
                        self.set_algo("independent")
                    if event.key == pygame.K_p:
                        self.set_algo("prioritized")
                    if event.key == pygame.K_c:
                        self.set_algo("cbs")
                    if event.unicode in ("1", "2", "3"):
                        self.set_scenario(event.unicode)
            self.update(dt)
            self.draw()
