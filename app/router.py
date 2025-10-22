from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db import db_helper
from schemas.responses import SuccessResponse, ErrorResponse
from . import service
from .security import verify_api_key

router = APIRouter()


@router.get(
    "/organizations/in-radius",
    response_model=SuccessResponse | ErrorResponse,
    dependencies=[Depends(verify_api_key)],
    summary="Получить организации в радиусе",
    description="""
Возвращает список организаций, которые находятся в заданном радиусе от указанной точки (широта и долгота).  
Используется географический поиск для отображения ближайших организаций.

**Параметры:**
- `lat` — широта центра поиска
- `lon` — долгота центра поиска
- `radius_km` — радиус (в километрах) вокруг точки

**Пример:** найти организации в радиусе 8 км от координат 55.84479724364538, 37.698429581209574.
""",
)
async def get_organizations_in_radius(
    lat: float = Query(...),
    lon: float = Query(...),
    radius_km: float = Query(...),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await service.get_organizations_in_radius(
        session=session,
        lat=lat,
        lon=lon,
        radius_km=radius_km,
    )


@router.get(
    "/organizations/search",
    response_model=SuccessResponse | ErrorResponse,
    dependencies=[Depends(verify_api_key)],
    summary="Получить организацию по ID",
    description="""
Возвращает подробную информацию об организации по её уникальному идентификатору.

**Параметры:**
- `organization_id` — идентификатор организации

**Пример:** найти организацию "ООО Рога и Копыта"
""",
)
async def search_organizations_by_name(
    name: str = Query(..., min_length=1),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await service.search_organization_by_name(
        session=session,
        name=name,
    )


@router.get(
    "/organizations/{organization_id}",
    response_model=SuccessResponse | ErrorResponse,
    dependencies=[Depends(verify_api_key)],
    summary="Получить организацию по ID",
    description="""
Возвращает подробную информацию об организации по её уникальному идентификатору.

**Параметры:**
- `organization_id` — идентификатор организации

**Пример:** найти организацию с id 3
""",
)
async def get_organization(
    organization_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await service.search_organization_by_id(
        session=session,
        organization_id=organization_id,
    )


@router.get(
    "/buildings/{building_id}/organizations",
    response_model=SuccessResponse | ErrorResponse,
    dependencies=[Depends(verify_api_key)],
    summary="Получить организации в здании",
    description="""
Возвращает список всех организаций, расположенных в указанном здании.

**Параметры:**
- `building_id` — идентификатор здания

**Пример:** найти организации в здании с id 1
""",
)
async def get_organizations_by_building(
    building_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await service.search_organizations_by_building(
        session=session,
        building_id=building_id,
    )


@router.get(
    "/activities/{activity_id}/organizations",
    response_model=SuccessResponse | ErrorResponse,
    dependencies=[Depends(verify_api_key)],
    summary="Получить организации по виду деятельности",
    description="""
Возвращает список организаций, относящихся к заданному виду деятельности.

Если указанный вид деятельности имеет вложенные подкатегории — в результатах также будут организации, относящиеся к ним.

**Пример:** при поиске по "Еда" будут найдены и "Молочная продукция", и "Мясная продукция", если они вложены в "Еда".

**Параметры:**
- `activity_name` — название вида деятельности

**Пример:** найти организации с видом деятельности "Еда"
""",
)
async def get_organizations_by_activity(
    activity_name: str,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await service.get_organizations_by_activity(
        session=session,
        activity_name=activity_name,
    )
