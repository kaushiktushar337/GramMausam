from __future__ import annotations

from dataclasses import dataclass

from shapely.geometry import Polygon, box


@dataclass
class GridCell:
    cell_id: str
    geometry: Polygon


def create_grid(minx: float, miny: float, maxx: float, maxy: float, cell_size: float) -> list[GridCell]:
    if cell_size <= 0:
        raise ValueError("cell_size must be greater than zero")

    cells = []
    x = minx
    column = 0
    while x < maxx:
        y = miny
        row = 0
        while y < maxy:
            cell = box(
                x,
                y,
                min(x + cell_size, maxx),
                min(y + cell_size, maxy),
            )
            cells.append(GridCell(f"g_{column}_{row}", cell))
            y += cell_size
            row += 1
        x += cell_size
        column += 1

    return cells


def clip_grid_to_polygon(grid: list[GridCell], polygon: Polygon) -> list[GridCell]:
    return [cell for cell in grid if cell.geometry.intersects(polygon)]
