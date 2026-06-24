from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import rasterio.transform

from terrain.dem_loader import DEMDataset
from terrain.region import EARTH_RADIUS_KM


@dataclass(frozen=True)
class Peak:
    latitude: float
    longitude: float
    elevation_m: float
    prominence_m: float


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    )
    return EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(a))


def _bbox_degrees(
    lat: float, lon: float, radius_km: float
) -> tuple[float, float, float, float]:
    lat_delta = radius_km / 111.0
    cos_lat = max(math.cos(math.radians(lat)), 1e-6)
    lon_delta = radius_km / (111.0 * cos_lat)
    return (
        lon - lon_delta,
        lat - lat_delta,
        lon + lon_delta,
        lat + lat_delta,
    )


def find_local_maxima(
    dem: DEMDataset,
    lat: float,
    lon: float,
    radius_km: float,
    min_prominence_m: float = 10.0,
) -> list[Peak]:
    west, south, east, north = _bbox_degrees(lat, lon, radius_km)

    row_start, col_start = rasterio.transform.rowcol(
        dem.transform, west, north
    )
    row_end, col_end = rasterio.transform.rowcol(dem.transform, east, south)

    row_min = max(0, min(row_start, row_end) - 1)
    row_max = min(dem.elevation.shape[0], max(row_start, row_end) + 2)
    col_min = max(0, min(col_start, col_end) - 1)
    col_max = min(dem.elevation.shape[1], max(col_start, col_end) + 2)

    window = dem.elevation[row_min:row_max, col_min:col_max]
    if window.size == 0:
        return []

    peaks: list[Peak] = []
    rows, cols = window.shape

    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            z = window[i, j]
            if np.isnan(z):
                continue

            neighbors = window[i - 1 : i + 2, j - 1 : j + 2]
            neighbor_mask = np.ones((3, 3), dtype=bool)
            neighbor_mask[1, 1] = False
            neighbor_vals = neighbors[neighbor_mask]
            if np.any(np.isnan(neighbor_vals)):
                continue

            if z <= np.max(neighbor_vals):
                continue

            prominence = float(z - np.min(neighbor_vals))
            if prominence < min_prominence_m:
                continue

            global_row = row_min + i
            global_col = col_min + j
            peak_lon, peak_lat = rasterio.transform.xy(
                dem.transform, global_row, global_col
            )

            if haversine_km(lat, lon, peak_lat, peak_lon) > radius_km:
                continue

            peaks.append(
                Peak(
                    latitude=round(peak_lat, 6),
                    longitude=round(peak_lon, 6),
                    elevation_m=round(float(z), 1),
                    prominence_m=round(prominence, 1),
                )
            )

    peaks.sort(key=lambda p: p.elevation_m, reverse=True)
    return peaks
