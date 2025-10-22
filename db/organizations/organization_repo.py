from typing import Sequence, Any

from sqlalchemy import select, literal_column, literal, func, Select
from sqlalchemy.orm import aliased, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from db.activities import Activity
from db.buildings import Building
from db.organizations import Organization
from db.association_tables import organization_activity_table


async def get_organization_by_name(
    name: str,
    session: AsyncSession,
) -> Organization | None:
    stmt = (
        select(Organization)
        .options(
            selectinload(Organization.building),
            selectinload(Organization.phone_numbers),
            selectinload(Organization.activities),
        )
        .where(Organization.name == name)
    )

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_organization_by_id(
    organization_by: int,
    session: AsyncSession,
) -> Organization | None:
    stmt = (
        select(Organization)
        .options(
            selectinload(Organization.building),
            selectinload(Organization.phone_numbers),
            selectinload(Organization.activities),
        )
        .where(Organization.id == organization_by)
    )

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_organizations_by_building(
    building_id: int,
    session: AsyncSession,
) -> Sequence[Organization]:
    stmt = (
        select(Organization)
        .options(
            selectinload(Organization.building),
            selectinload(Organization.phone_numbers),
            selectinload(Organization.activities),
        )
        .where(Organization.building_id == building_id)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


EARTH_RADIUS_KM = 6371.0


async def get_organizations_in_radius(
    lat: float,
    lon: float,
    radius_km: float,
    session: AsyncSession,
) -> Sequence[Organization]:
    # Выборка зданий в радиусе (формула упрощенного гаверсинуса)
    stmt = select(Building).where(
        EARTH_RADIUS_KM
        * func.acos(
            func.cos(func.radians(lat))
            * func.cos(func.radians(Building.latitude))
            * func.cos(func.radians(Building.longitude) - func.radians(lon))
            + func.sin(func.radians(lat)) * func.sin(func.radians(Building.latitude))
        )
        <= radius_km
    )

    result = await session.execute(stmt)
    buildings = result.scalars().all()

    if not buildings:
        return []

    building_ids = [b.id for b in buildings]

    stmt = (
        select(Organization)
        .options(
            selectinload(Organization.building),
            selectinload(Organization.activities),
            selectinload(Organization.phone_numbers),
        )
        .where(Organization.building_id.in_(building_ids))
    )

    result = await session.execute(stmt)
    return result.scalars().all()


async def get_activity_descendants(
    root_name: str,
    session: AsyncSession,
    max_depth: int = 3,
) -> Select[tuple[Any]] | Select | list:
    # Получаем корневой вид деятельности (например, "Еда")
    res = await session.execute(select(Activity).where(Activity.name == root_name))
    root_activity = res.scalar_one_or_none()

    if not root_activity:
        return []

    # Рекурсивный CTE
    activity_cte = (
        select(
            Activity.id.label("id"),
            Activity.parent_id.label("parent_id"),
            literal_column("1").label("depth"),
        )
        .where(Activity.id == root_activity.id)
        .cte(name="activity_cte", recursive=True)
    )

    activity_alias = aliased(activity_cte)

    children = (
        select(
            Activity.id, Activity.parent_id, (activity_alias.c.depth + 1).label("depth")
        )
        .join(activity_alias, Activity.parent_id == activity_alias.c.id)
        .where(activity_alias.c.depth < max_depth)
    )

    activity_cte = activity_cte.union_all(children)

    # Получаем ID всех подходящих видов деятельности
    activity_ids_subquery = select(activity_cte.c.id)

    return activity_ids_subquery


async def get_organizations_by_activity(
    activity_name: str,
    session: AsyncSession,
) -> Sequence[Organization]:
    activity_ids_subquery = await get_activity_descendants(activity_name, session)

    orgs_query = (
        select(Organization)
        .options(
            selectinload(Organization.building),
            selectinload(Organization.activities),
            selectinload(Organization.phone_numbers),
        )
        .join(
            organization_activity_table,
            Organization.id == organization_activity_table.c.organization_id,
        )
        .where(organization_activity_table.c.activity_id.in_(activity_ids_subquery))
        .distinct()
    )

    res = await session.execute(orgs_query)
    return res.scalars().all()
