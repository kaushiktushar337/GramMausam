from pathlib import Path

import numpy as np
import rasterio


FILE_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "raw"
    / "chirps"
    / "chirps-v3.0.sat.2025.04.24.tif"
)


def main():
    if not FILE_PATH.exists():
        raise FileNotFoundError(
            f"CHIRPS file not found: {FILE_PATH}"
        )

    with rasterio.open(FILE_PATH) as src:
        print("File:", FILE_PATH.name)
        print("Driver:", src.driver)
        print("Width:", src.width)
        print("Height:", src.height)
        print("Bands:", src.count)
        print("CRS:", src.crs)
        print("Bounds:", src.bounds)
        print("Resolution:", src.res)
        print("NoData metadata:", src.nodata)

        rainfall = src.read(1)

        valid_rainfall = rainfall[rainfall > -9000]

        print("Rainfall array shape:", rainfall.shape)
        print("Total pixels:", rainfall.size)
        print("Valid pixels:", valid_rainfall.size)
        print("Missing/sentinel pixels:", rainfall.size - valid_rainfall.size)

        print(
            "Minimum valid rainfall:",
            float(valid_rainfall.min())
        )

        print(
            "Maximum valid rainfall:",
            float(valid_rainfall.max())
        )

        print(
            "Mean valid rainfall:",
            float(valid_rainfall.mean())
        )


if __name__ == "__main__":
    main()