from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from typing import Optional, List, TYPE_CHECKING

from db.base import Base
from db.association_tables import organization_activity_table

if TYPE_CHECKING:
    from db.organizations import Organization


class Activity(Base):
    __tablename__ = "activities"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("activities.id"), nullable=True
    )

    # Рекурсивная связь (родитель)
    parent: Mapped[Optional["Activity"]] = relationship(
        back_populates="children", remote_side="Activity.id"
    )

    # Рекурсивная связь (потомок)
    children: Mapped[List["Activity"]] = relationship(
        back_populates="parent", cascade="all, delete-orphan"
    )

    organizations: Mapped[list["Organization"]] = relationship(
        secondary=organization_activity_table, back_populates="activities"
    )

    def __repr__(self):
        return f"<Activity(name='{self.name}', parent_id={self.parent_id})>"
