from pathlib import Path

import rasterio
from rasterio.windows import from_bounds


FILE_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "raw"
    / "chirps"
    / "chirps-v3.0.sat.2025.04.24.tif"
)

OUTPUT_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "processed"
    / "chirps_india_2025-04-24.tif"
)


def main():
    with rasterio.open(FILE_PATH) as src:

        # India approximate bounding box
        west = 68.0
        south = 6.0
        east = 98.0
        north = 38.0

        window = from_bounds(
            west,
            south,
            east,
            north,
            transform=src.transform,
        )

        window = window.round_offsets().round_lengths()

        rainfall = src.read(1, window=window)

        transform = src.window_transform(window)

        profile = src.profile.copy()

        profile.update(
            {
                "height": rainfall.shape[0],
                "width": rainfall.shape[1],
                "transform": transform,
                "compress": "lzw",
            }
        )

        OUTPUT_PATH.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with rasterio.open(
            OUTPUT_PATH,
            "w",
            **profile,
        ) as dst:
            dst.write(rainfall, 1)

        print("Input:", FILE_PATH.name)
        print("Output:", OUTPUT_PATH)
        print("Subset shape:", rainfall.shape)
        print("Resolution:", src.res)
        print("CRS:", src.crs)


if __name__ == "__main__":
    main()