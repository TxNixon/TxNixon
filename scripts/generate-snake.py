"""Generate a script-free SVG Snake replay for the GitHub profile.

Run: python scripts/generate-snake.py
Each frame is derived from the same board state: food, growth and score stay
in sync. Only SVG visibility is animated; no independent moving parts drift.
"""

from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
CELL, LEFT, TOP = 28, 124, 72
STEP = 0.16
WAYPOINTS = [(3, 2), (12, 2), (12, 5), (22, 5), (22, 1),
             (30, 1), (30, 8), (3, 8), (3, 2)]
FOOD_STEPS = [9, 22, 34, 49, 66]


def route_cells():
    cells = []
    for (x, y), (end_x, end_y) in zip(WAYPOINTS, WAYPOINTS[1:]):
        dx = (end_x > x) - (end_x < x)
        dy = (end_y > y) - (end_y < y)
        assert (dx == 0) != (dy == 0), "Route must follow grid axes"
        while (x, y) != (end_x, end_y):
            cells.append((x, y))
            x, y = x + dx, y + dy
    assert len(set(cells)) == len(cells), "Route crosses itself"
    return cells


def frame(step, route):
    eaten = sum(step >= food for food in FOOD_STEPS)
    length = 5 + eaten
    snake = [route[(step - offset) % len(route)] for offset in range(length)]
    assert len(set(snake)) == length, "Snake overlaps itself"
    parts = [f'<text x="1104" y="40" text-anchor="end" fill="#dce7e0" '
             f'font-size="14">{eaten * 10:03d}</text>']
    for offset, (x, y) in reversed(list(enumerate(snake))):
        px, py = LEFT + x * CELL + 2, TOP + y * CELL + 2
        color = "#d1f7a3" if offset == 0 else ("#91bb72" if offset < 4 else "#638953")
        parts.append(f'<rect x="{px}" y="{py}" width="24" height="24" '
                     f'rx="4" fill="{color}"/>')
    hx, hy = snake[0]
    prev_x, prev_y = route[(step - 1) % len(route)]
    dx, dy = hx - prev_x, hy - prev_y
    assert abs(dx) + abs(dy) == 1, "Snake jumps between cells"
    eye_offsets = ([(18, 7), (18, 17)] if dx == 1 else
                   [(6, 7), (6, 17)] if dx == -1 else
                   [(7, 18), (17, 18)] if dy == 1 else [(7, 6), (17, 6)])
    for ex, ey in eye_offsets:
        parts.append(f'<rect x="{LEFT + hx * CELL + ex}" y="{TOP + hy * CELL + ey}" '
                     'width="3" height="3" rx=".5" fill="#16221b"/>')
    next_food = next((food for food in FOOD_STEPS if food > step), None)
    if next_food is not None:
        fx, fy = route[next_food]
        assert (fx, fy) not in snake, "Food appears inside the snake"
        px, py = LEFT + fx * CELL, TOP + fy * CELL
        parts.extend([
            f'<rect x="{px + 6}" y="{py + 7}" width="16" height="16" rx="4" fill="#e7a16c"/>',
            f'<path d="M{px + 14} {py + 7}v-4h5" fill="none" stroke="#bcd39d" stroke-width="2"/>',
        ])
    if step == len(route):
        parts.append('<rect x="472" y="164" width="256" height="72" rx="8" '
                     'fill="#111c17" stroke="#395142"/>')
        parts.append('<text x="600" y="194" text-anchor="middle" fill="#d1f7a3" '
                     'font-size="16" letter-spacing="2">ROUND CLEAR</text>')
        parts.append('<text x="600" y="216" text-anchor="middle" fill="#95a69b" '
                     'font-size="11">50 POINTS / PLAY AGAIN</text>')
    return "\n      ".join(parts)


def generate():
    route = route_cells()
    steps = list(range(len(route) + 1)) + [len(route)] * 6
    duration = len(steps) * STEP
    frames = []
    for index, step in enumerate(steps):
        frames.append(f'<g class="frame f{index}" style="animation-delay:{index * STEP:.2f}s">'
                      f'\n      {frame(step, route)}\n    </g>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="410" viewBox="0 0 1200 410" role="img" aria-labelledby="title desc">
  <title id="title">Snake / a little break between builds</title>
  <desc id="desc">An autoplay Snake replay. The snake eats five pieces of food, grows from five to ten cells, and scores fifty points before a new round. No player input or contribution data.</desc>
  <defs>
    <pattern id="grid" x="124" y="72" width="28" height="28" patternUnits="userSpaceOnUse">
      <path d="M28 0H0V28" fill="none" stroke="#223129" stroke-width=".7"/>
    </pattern>
    <style>
      .frame {{ visibility:hidden; animation:frame {duration:.2f}s steps(1,end) infinite; }}
      .f0 {{ visibility:visible; }}
      @keyframes frame {{ 0% {{ visibility:visible; }} {100 / len(steps):.12f}%,100% {{ visibility:hidden; }} }}
      @media (prefers-reduced-motion:reduce) {{
        .frame {{ animation:none; visibility:hidden; }}
        .f0 {{ visibility:visible; }}
      }}
    </style>
  </defs>
  <rect x="1" y="1" width="1198" height="408" rx="14" fill="#0d1511" stroke="#29392f"/>
  <g font-family="monospace">
    <text x="96" y="40" fill="#d1f7a3" font-size="15" letter-spacing="3">SNAKE</text>
    <text x="190" y="40" fill="#81958a" font-size="12">/ 01</text>
    <text x="1052" y="40" text-anchor="end" fill="#81958a" font-size="11" letter-spacing="1.5">SCORE</text>
    <rect x="124" y="72" width="952" height="280" rx="4" fill="#111c17" stroke="#2c3d31"/>
    <rect x="124" y="72" width="952" height="280" fill="url(#grid)"/>
    {chr(10).join(frames)}
    <circle cx="100" cy="385" r="3" fill="#91bb72"/>
    <text x="113" y="389" fill="#81958a" font-size="11" letter-spacing="1">AUTOPLAY</text>
    <text x="1104" y="389" text-anchor="end" fill="#81958a" font-size="11">A LITTLE BREAK BETWEEN BUILDS.</text>
  </g>
</svg>
'''
    ElementTree.fromstring(svg)
    (ROOT / "snake.svg").write_text(svg, encoding="utf-8")
    print(f"Generated snake.svg: {len(steps)} frames, {duration:.2f}s loop, 5 meals, 50 points.")


if __name__ == "__main__":
    generate()
