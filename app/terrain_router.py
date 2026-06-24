from fastapi import APIRouter, Depends, Query

from app.security import verify_api_key
from schemas.terrain import TerrainErrorResponse, TerrainSuccessResponse
from terrain import service

router = APIRouter()


@router.get(
    "/local-maxima",
    response_model=TerrainSuccessResponse | TerrainErrorResponse,
    dependencies=[Depends(verify_api_key)],
    summary="Локальные максимумы рельефа в радиусе",
    description="""
Возвращает точки с локальными максимумами высоты рельефа в заданном радиусе
от указанной координаты.

Данные: Copernicus DEM GLO-30, регион **южный берег Крыма** (Ялта — Ай-Петри — Форос).

**Параметры:**
- `lat` — широта центра поиска (должна попадать в bbox региона)
- `lon` — долгота центра поиска
- `radius_km` — радиус поиска в километрах (0.1–50)
- `min_prominence_m` — минимальный «выступ» пика над соседними ячейками (по умолчанию 10 м)

**Пример:** найти вершины в радиусе 3 км от Ай-Петри (44.452, 34.059).
""",
)
async def get_local_maxima(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(..., ge=0.1, le=50),
    min_prominence_m: float = Query(10.0, ge=0),
):
    return await service.get_local_maxima(
        lat=lat,
        lon=lon,
        radius_km=radius_km,
        min_prominence_m=min_prominence_m,
    )
