from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import Affine

from terrain.region import BBOX, DEM_PATH, REGION_NAME

logger = logging.getLogger(__name__)

_dem: DEMDataset | None = None


@dataclass(frozen=True)
class DEMDataset:
    name: str
    elevation: np.ndarray
    transform: Affine
    nodata: float | None
    bounds: tuple[float, float, float, float]  # west, south, east, north

    def contains(self, lat: float, lon: float) -> bool:
        west, south, east, north = self.bounds
        return south <= lat <= north and west <= lon <= east


def load_dem(path: Path = DEM_PATH) -> DEMDataset | None:
    global _dem

    if not path.is_file():
        logger.warning("DEM file not found: %s", path)
        _dem = None
        return None

    with rasterio.open(path) as src:
        elevation = src.read(1).astype(np.float64)
        nodata = src.nodata
        if nodata is not None:
            elevation[elevation == nodata] = np.nan

        _dem = DEMDataset(
            name=REGION_NAME,
            elevation=elevation,
            transform=src.transform,
            nodata=nodata,
            bounds=(src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top),
        )

    logger.info(
        "Loaded DEM '%s' from %s (%dx%d px)",
        REGION_NAME,
        path,
        _dem.elevation.shape[1],
        _dem.elevation.shape[0],
    )
    return _dem


def get_dem() -> DEMDataset | None:
    return _dem


def point_in_region(lat: float, lon: float) -> bool:
    west, south, east, north = BBOX
    return south <= lat <= north and west <= lon <= east
