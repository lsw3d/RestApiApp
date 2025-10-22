from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

if TYPE_CHECKING:
    from db.organizations import Organization


class Building(Base):
    __tablename__ = "buildings"

    address: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    organizations: Mapped[list["Organization"]] = relationship(
        back_populates="building"
    )

    def __repr__(self):
        return (
            f"<Building(address='{self.address}', "
            f"lat={self.latitude}, lon={self.longitude})>"
        )
