from pydantic import BaseModel


class LocalMaximaOut(BaseModel):
    latitude: float
    longitude: float
    elevation_m: float
    prominence_m: float


class LocalMaximaMeta(BaseModel):
    region: str
    count: int
    center_latitude: float
    center_longitude: float
    radius_km: float
    min_prominence_m: float


class TerrainSuccessResponse(BaseModel):
    result: bool = True
    data: list[LocalMaximaOut]
    meta: LocalMaximaMeta


class TerrainErrorResponse(BaseModel):
    result: bool = False
    detail: str | None = None
