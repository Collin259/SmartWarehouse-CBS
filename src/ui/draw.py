from __future__ import annotations
from typing import List
import pygame
from ..planner import Agent, Path
from ..planner.grid import Grid
from ..sim.world import World
from ..sim.robot import RobotSim

def draw_world(screen: pygame.Surface, world: World, grid: Grid):
    screen.fill((248, 249, 250))
    for y in range(grid.h):
        for x in range(grid.w):
            rect = pygame.Rect(*world.cell_rect_px((x, y)))
            pygame.draw.rect(screen, (235, 237, 240), rect, width=1)
    for (x, y) in grid.obstacles:
        rect = pygame.Rect(*world.cell_rect_px((x, y)))
        pygame.draw.rect(screen, (40, 40, 40), rect)

def draw_goals(screen: pygame.Surface, world: World, agents: List[Agent]):
    for a in agents:
        rect = pygame.Rect(*world.cell_rect_px(a.goal))
        pygame.draw.rect(screen, (210, 210, 210), rect)
        pygame.draw.rect(screen, (150, 150, 150), rect, width=2)

def draw_paths(screen: pygame.Surface, world: World, paths: List[Path]):
    for p in paths:
        if len(p) < 2:
            continue
        pts = [world.grid_to_px_center(c) for c in p]
        pygame.draw.lines(screen, (140, 140, 140), False, pts, width=2)

def draw_robots(screen: pygame.Surface, robots: List[RobotSim], radius: int = 14):
    font = pygame.font.SysFont(None, 18)
    for r in robots:
        pygame.draw.circle(screen, r.color, (int(r.pos[0]), int(r.pos[1])), radius)
        pygame.draw.circle(screen, (30, 30, 30), (int(r.pos[0]), int(r.pos[1])), radius, width=2)
        label = font.render(r.name, True, (0, 0, 0))
        screen.blit(label, (int(r.pos[0]) - label.get_width()//2, int(r.pos[1]) - label.get_height()//2))

def draw_sidebar(screen: pygame.Surface, world: World, title: str, algo: str, running: bool, speed: float, sim_time: float, info_lines: List[str]):
    w, h = screen.get_size()
    x0 = w - world.cfg.sidebar_px
    panel = pygame.Rect(x0, 0, world.cfg.sidebar_px, h)
    pygame.draw.rect(screen, (255, 255, 255), panel)
    pygame.draw.rect(screen, (220, 220, 220), panel, width=2)

    font_h = pygame.font.SysFont(None, 22)
    font = pygame.font.SysFont(None, 20)

    y = 16
    header = [title, f"Algo: {algo}", "Running" if running else "Paused", f"Speed: {speed:.2f}x", f"Sim t: {sim_time:.1f}s"]
    for line in header:
        surf = font_h.render(line, True, (0, 0, 0))
        screen.blit(surf, (x0 + 12, y))
        y += 26

    y += 8
    for line in info_lines:
        surf = font.render(line, True, (30, 30, 30))
        screen.blit(surf, (x0 + 12, y))
        y += 22

    y = h - 160
    help_lines = [
        "Space: Play/Pause",
        "I/P/C: Algo switch",
        "1/2/3: Demos",
        "+/-: Speed",
        "O: Toggle paths",
        "R: Reset time",
        "Esc: Quit",
    ]
    for line in help_lines:
        surf = font.render(line, True, (80, 80, 80))
        screen.blit(surf, (x0 + 12, y))
        y += 20
