import argparse

import geopandas as gpd
from shapely.geometry import Polygon

from app.geo.grid import create_grid


parser = argparse.ArgumentParser(description="Create a fine-resolution grid from a bounding box.")
parser.add_argument("--minx", type=float, required=True)
parser.add_argument("--miny", type=float, required=True)
parser.add_argument("--maxx", type=float, required=True)
parser.add_argument("--maxy", type=float, required=True)
parser.add_argument("--cell-size", type=float, default=0.01)
parser.add_argument("--output", default="data/processed/grid.geojson")
args = parser.parse_args()

grid = create_grid(args.minx, args.miny, args.maxx, args.maxy, args.cell_size)
gdf = gpd.GeoDataFrame(
    {"cell_id": [cell.cell_id for cell in grid]},
    geometry=[cell.geometry for cell in grid],
    crs="EPSG:4326",
)
gdf.to_file(args.output, driver="GeoJSON")
print(f"Created {len(gdf)} grid cells at {args.output}")
