from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.organizations import organization_repo
from schemas.responses import SuccessResponse, ErrorResponse, OrganizationOut


async def search_organization_by_name(
    name: str,
    session: AsyncSession,
) -> SuccessResponse | ErrorResponse:
    try:
        organization = await organization_repo.get_organization_by_name(
            name=name,
            session=session,
        )
        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Организация с именем '{name}' не найдена",
            )
        return SuccessResponse(
            data=OrganizationOut.model_validate(organization),
        )
    except HTTPException:
        raise
    except Exception as e:
        return ErrorResponse(
            detail=str(e),
        )


async def search_organization_by_id(
    organization_id: int,
    session: AsyncSession,
) -> SuccessResponse | ErrorResponse:
    try:
        organization = await organization_repo.get_organization_by_id(
            organization_by=organization_id,
            session=session,
        )
        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Организация с id '{organization_id}' не найдена",
            )
        return SuccessResponse(
            data=OrganizationOut.model_validate(organization),
        )
    except HTTPException:
        raise
    except Exception as e:
        return ErrorResponse(
            detail=str(e),
        )


async def search_organizations_by_building(
    building_id: int,
    session: AsyncSession,
) -> SuccessResponse | ErrorResponse:
    try:
        organizations = await organization_repo.get_organizations_by_building(
            building_id=building_id,
            session=session,
        )
        orgs = [
            OrganizationOut.model_validate(organization)
            for organization in organizations
        ]
        return SuccessResponse(
            data=orgs,
        )
    except Exception as e:
        return ErrorResponse(
            detail=str(e),
        )


async def get_organizations_by_activity(
    activity_name: str,
    session: AsyncSession,
) -> SuccessResponse | ErrorResponse:
    try:
        organizations = await organization_repo.get_organizations_by_activity(
            activity_name=activity_name,
            session=session,
        )
        orgs = [
            OrganizationOut.model_validate(organization)
            for organization in organizations
        ]
        return SuccessResponse(
            data=orgs,
        )
    except Exception as e:
        return ErrorResponse(
            detail=str(e),
        )


async def get_organizations_in_radius(
    lat: float,
    lon: float,
    radius_km: float,
    session: AsyncSession,
) -> SuccessResponse | ErrorResponse:
    try:
        organizations = await organization_repo.get_organizations_in_radius(
            lat=lat,
            lon=lon,
            radius_km=radius_km,
            session=session,
        )
        orgs = [
            OrganizationOut.model_validate(organization)
            for organization in organizations
        ]
        return SuccessResponse(
            data=orgs,
        )
    except Exception as e:
        return ErrorResponse(
            detail=str(e),
        )
