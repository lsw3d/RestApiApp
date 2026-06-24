from fastapi import HTTPException, status

from schemas.terrain import LocalMaximaMeta, LocalMaximaOut, TerrainSuccessResponse
from terrain.dem_loader import get_dem, point_in_region
from terrain.local_maxima import find_local_maxima


async def get_local_maxima(
    lat: float,
    lon: float,
    radius_km: float,
    min_prominence_m: float,
) -> TerrainSuccessResponse:
    dem = get_dem()
    if dem is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="DEM data not loaded. Run: python scripts/download_dem.py",
        )

    if not point_in_region(lat, lon):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Point ({lat}, {lon}) is outside region '{dem.name}' "
                f"bbox {dem.bounds}"
            ),
        )

    peaks = find_local_maxima(
        dem=dem,
        lat=lat,
        lon=lon,
        radius_km=radius_km,
        min_prominence_m=min_prominence_m,
    )

    return TerrainSuccessResponse(
        data=[
            LocalMaximaOut(
                latitude=p.latitude,
                longitude=p.longitude,
                elevation_m=p.elevation_m,
                prominence_m=p.prominence_m,
            )
            for p in peaks
        ],
        meta=LocalMaximaMeta(
            region=dem.name,
            count=len(peaks),
            center_latitude=lat,
            center_longitude=lon,
            radius_km=radius_km,
            min_prominence_m=min_prominence_m,
        ),
    )
