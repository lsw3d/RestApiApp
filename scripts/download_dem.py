#!/usr/bin/env python3
"""Download and clip Copernicus DEM GLO-30 for the Crimea south coast region."""

from __future__ import annotations

import sys
import tempfile
import urllib.request
from pathlib import Path

import rasterio
from rasterio.merge import merge
from rasterio.windows import from_bounds

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from terrain.region import BBOX, DEM_PATH  # noqa: E402

COPERNICUS_BASE = (
    "https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com"
)


def _tile_url(lat: int, lon: int) -> str:
    ns = "N" if lat >= 0 else "S"
    ew = "E" if lon >= 0 else "W"
    name = (
        f"Copernicus_DSM_COG_10_{ns}{abs(lat):02d}_00_"
        f"{ew}{abs(lon):03d}_00_DEM"
    )
    return f"{COPERNICUS_BASE}/{name}/{name}.tif"


def _tiles_for_bbox(west: float, south: float, east: float, north: float) -> list[tuple[int, int]]:
    lat_min = int(south)
    lat_max = int(north)
    lon_min = int(west)
    lon_max = int(east)
    return [
        (lat, lon)
        for lat in range(lat_min, lat_max + 1)
        for lon in range(lon_min, lon_max + 1)
    ]


def _download_tile(lat: int, lon: int, dest: Path) -> None:
    url = _tile_url(lat, lon)
    print(f"Downloading {url} ...")
    urllib.request.urlretrieve(url, dest)


def download_dem(output: Path = DEM_PATH) -> Path:
    if output.exists():
        print(f"DEM already exists at {output}, skipping download.")
        return output

    west, south, east, north = BBOX
    tiles = _tiles_for_bbox(west, south, east, north)

    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        tile_paths: list[Path] = []

        for lat, lon in tiles:
            tile_path = tmp / f"tile_{lat}_{lon}.tif"
            _download_tile(lat, lon, tile_path)
            tile_paths.append(tile_path)

        datasets = [rasterio.open(p) for p in tile_paths]
        try:
            mosaic, mosaic_transform = merge(datasets)
            meta = datasets[0].meta.copy()
        finally:
            for ds in datasets:
                ds.close()

        meta.update(
            {
                "driver": "GTiff",
                "height": mosaic.shape[1],
                "width": mosaic.shape[2],
                "transform": mosaic_transform,
                "count": 1,
                "dtype": mosaic.dtype,
            }
        )

        merged_path = tmp / "merged.tif"
        with rasterio.open(merged_path, "w", **meta) as dst:
            dst.write(mosaic)

        with rasterio.open(merged_path) as src:
            window = from_bounds(west, south, east, north, src.transform)
            data = src.read(1, window=window)
            transform = src.window_transform(window)
            clipped_meta = src.meta.copy()
            clipped_meta.update(
                {
                    "height": data.shape[0],
                    "width": data.shape[1],
                    "transform": transform,
                }
            )

        with rasterio.open(output, "w", **clipped_meta) as dst:
            dst.write(data, 1)

        with rasterio.open(output) as src:
            if src.crs is None or src.crs.to_epsg() != 4326:
                print(f"Warning: CRS is {src.crs}, expected EPSG:4326")
            print(
                f"Saved {output} — {src.width}x{src.height} px, "
                f"bounds {src.bounds}, nodata={src.nodata}"
            )

    return output


if __name__ == "__main__":
    download_dem()
