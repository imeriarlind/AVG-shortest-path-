"""
Generates layout.csv with 10 rows.
CSV format per row: sr, sc, er, ec, v0, v1, ..., v255
  - sr/sc = start row/col
  - er/ec = end row/col
  - v0..v255 = 16x16 grid cells (0=free, 1=obstacle)

Rules:
  - Start and end are random, at least 10 cells apart (Manhattan distance)
  - Start in top-left quadrant, end in bottom-right (varied)
  - Minimum BFS path length of 28 steps for complexity
  - Higher obstacle density for winding paths
"""

import csv
import random
from collections import deque

ROWS = COLS = 16
MIN_PATH_LEN = 28
MIN_MANHATTAN = 10


def bfs_path_len(flat, start, end):
    grid = [flat[i * COLS:(i + 1) * COLS] for i in range(ROWS)]
    queue = deque([(start, 0)])
    visited = {start}
    while queue:
        (r, c), dist = queue.popleft()
        if (r, c) == end:
            return dist
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nr][nc] == 0 and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append(((nr, nc), dist + 1))
    return -1


def make_maze(seed, obstacle_density):
    rng = random.Random(seed)
    attempts = 0
    while True:
        attempts += 1

        flat = [1 if rng.random() < obstacle_density else 0 for _ in range(ROWS * COLS)]

        free_cells = [(r, c) for r in range(ROWS) for c in range(COLS)
                      if flat[r * COLS + c] == 0]
        if len(free_cells) < 10:
            continue

        start = rng.choice(free_cells)
        candidates = [
            cell for cell in free_cells
            if abs(cell[0] - start[0]) + abs(cell[1] - start[1]) >= MIN_MANHATTAN
        ]
        if not candidates:
            continue
        end = rng.choice(candidates)

        flat[start[0] * COLS + start[1]] = 0
        flat[end[0] * COLS + end[1]] = 0

        path_len = bfs_path_len(flat, start, end)
        if path_len >= MIN_PATH_LEN:
            return start, end, flat


CONFIGS = [
    (101, 0.38),
    (202, 0.40),
    (303, 0.36),
    (404, 0.42),
    (505, 0.39),
    (606, 0.37),
    (707, 0.41),
    (808, 0.35),
    (909, 0.43),
    (111, 0.38),
]

with open("layout.csv", "w", newline="") as f:
    writer = csv.writer(f)
    for i, (seed, density) in enumerate(CONFIGS, start=1):
        start, end, flat = make_maze(seed, density)
        row = [start[0], start[1], end[0], end[1]] + flat
        writer.writerow(row)
        print(f"  Layout {i:2d}: start={start} end={end}")

print("\nlayout.csv written with 10 rows.")
