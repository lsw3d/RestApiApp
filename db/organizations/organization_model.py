from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey

from db.association_tables import organization_activity_table
from db.base import Base

if TYPE_CHECKING:
    from db.buildings import Building
    from db.activities import Activity
    from db.phone_numbers import PhoneNumber


class Organization(Base):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Организация находится в одном здании
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"), nullable=False)
    building: Mapped["Building"] = relationship(back_populates="organizations")

    # Организация может иметь несколько номеров телефона
    phone_numbers: Mapped[list["PhoneNumber"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )

    # Организация может заниматься несколькими видами деятельности
    activities: Mapped[list["Activity"]] = relationship(
        secondary=organization_activity_table, back_populates="organizations"
    )

    def __repr__(self):
        return f"<Organization(name='{self.name}')>"
