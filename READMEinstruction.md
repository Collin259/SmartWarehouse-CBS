CBS MAPF — Pygame Smooth-Motion Simulator
========================================

This project plans collision-free multi-robot routes on a grid using Conflict-Based Search (CBS),
then simulates the robots moving smoothly between grid cell centers in pygame.

Install
-------
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

Run
---
python -m src.main_pygame --scenario scenarios/demo_02_intersection.json --algo cbs

Controls
--------
Space  : Play/Pause
R      : Reset simulation time (keeps same planned paths)
1/2/3  : Load demo scenarios 1/2/3 (replans)
I/P/C  : Switch algo (Independent / Prioritized / CBS) and replan
+/-    : Speed up / slow down simulation
O      : Toggle path overlay
Esc    : Quit
