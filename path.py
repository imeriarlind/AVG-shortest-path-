import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from collections import deque
import csv
import os

ROWS = COLS = 16
CSV_FILE   = "layout.csv"
OUTPUT_DIR = "pathPhotos"
BLOCK_DISTANCE_M = 1.0
AGV_SPEED_MPS = 0.5


def bfs(grid, start, end):
    rows, cols = len(grid), len(grid[0])
    queue = deque([(start, [start])])
    visited = {start}
    while queue:
        (row, col), path = queue.popleft()
        if (row, col) == end:
            return path
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if (
                0 <= nr < rows
                and 0 <= nc < cols
                and grid[nr][nc] == 0
                and (nr, nc) not in visited
            ):
                visited.add((nr, nc))
                queue.append(((nr, nc), path + [(nr, nc)]))
    return None


def compute_path_metrics(path, block_distance_m=BLOCK_DISTANCE_M, speed_mps=AGV_SPEED_MPS):
    if not path:
        return 0, 0.0, None

    steps = len(path) - 1
    distance_m = steps * block_distance_m
    time_s = distance_m / speed_mps if speed_mps > 0 else None
    return steps, distance_m, time_s


def visualize_and_save(grid, path, start, end, filename):
    rows, cols = len(grid), len(grid[0])
    color_map = np.zeros((rows, cols, 3))

    for r in range(rows):
        for c in range(cols):
            color_map[r, c] = [0.18, 0.18, 0.18] if grid[r][c] == 1 else [0.96, 0.96, 0.96]

    if path:
        for r, c in path:
            color_map[r, c] = [0.18, 0.55, 0.93]

    sr, sc = start
    er, ec = end
    color_map[sr, sc] = [0.13, 0.75, 0.37]
    color_map[er, ec] = [0.93, 0.26, 0.26]

    fig, ax = plt.subplots(figsize=(9, 9))
    ax.imshow(color_map, interpolation="nearest")

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                ax.text(c, r, "■", ha="center", va="center",
                        fontsize=9, color="white", alpha=0.5)

    arrow_map = {(0, 1): "→", (0, -1): "←", (1, 0): "↓", (-1, 0): "↑"}
    if path:
        for i, (r, c) in enumerate(path):
            if (r, c) in (start, end):
                continue
            pr, pc = path[i - 1]
            symbol = arrow_map.get((r - pr, c - pc), "·")
            ax.text(c, r, symbol, ha="center", va="center",
                    fontsize=10, color="white", fontweight="bold")

    ax.text(sc, sr, "S", ha="center", va="center",
            fontsize=12, color="white", fontweight="bold")
    ax.text(ec, er, "E", ha="center", va="center",
            fontsize=12, color="white", fontweight="bold")

    ax.set_xticks(np.arange(-0.5, cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, rows, 1), minor=True)
    ax.grid(which="minor", color="gray", linewidth=0.5, alpha=0.4)
    ax.tick_params(which="minor", size=0)
    ax.set_xticks(range(cols))
    ax.set_yticks(range(rows))
    ax.set_xticklabels(range(cols), fontsize=8)
    ax.set_yticklabels(range(rows), fontsize=8)

    steps, distance_m, time_s = compute_path_metrics(path)
    if path:
        time_label = f"{time_s:.2f} s" if time_s is not None else "N/A (speed must be > 0)"
        status = f"Shortest path: {steps} steps | Distance: {distance_m:.2f} m | Time: {time_label}"
    else:
        status = "No path found"
    label = os.path.splitext(os.path.basename(filename))[0]
    ax.set_title(
        f"AGV BFS — {label}  |  Start {start} → End {end}\n{status}",
        fontsize=12, fontweight="bold", pad=12
    )

    legend_patches = [
        mpatches.Patch(color=[0.13, 0.75, 0.37], label="Start (S)"),
        mpatches.Patch(color=[0.93, 0.26, 0.26], label="End (E)"),
        mpatches.Patch(color=[0.18, 0.55, 0.93], label="BFS Path"),
        mpatches.Patch(color=[0.18, 0.18, 0.18], label="Obstacle"),
        mpatches.Patch(color=[0.96, 0.96, 0.96], label="Free cell"),
    ]
    ax.legend(handles=legend_patches, loc="upper right",
              bbox_to_anchor=(1.18, 1), fontsize=9)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()


def load_grids_from_csv(csv_path):
    layouts = []
    with open(csv_path, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            values = [int(v) for v in row]
            sr, sc, er, ec = values[0], values[1], values[2], values[3]
            flat = values[4:]
            grid = [flat[i * COLS:(i + 1) * COLS] for i in range(ROWS)]
            layouts.append(((sr, sc), (er, ec), grid))
    return layouts


if __name__ == "__main__":
    layouts = load_grids_from_csv(CSV_FILE)
    print(f"Loaded {len(layouts)} layouts from {CSV_FILE}\n")
    print(f"Block distance: {BLOCK_DISTANCE_M} m | AGV speed: {AGV_SPEED_MPS} m/s\n")

    for idx, (start, end, grid) in enumerate(layouts, start=1):
        path = bfs(grid, start, end)
        filename = os.path.join(OUTPUT_DIR, f"path{idx}.png")
        visualize_and_save(grid, path, start, end, filename)
        steps, distance_m, time_s = compute_path_metrics(path)
        if path:
            time_label = f"{time_s:.2f} s" if time_s is not None else "N/A (speed must be > 0)"
            status = f"{steps} steps, {distance_m:.2f} m, {time_label}"
        else:
            status = "no path found"
        print(f"  path{idx}.png — start={start} end={end} — {status}")

    print("\nDone.")
