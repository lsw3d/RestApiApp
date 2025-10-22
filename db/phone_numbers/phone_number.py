from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey

from db.base import Base

if TYPE_CHECKING:
    from db.organizations import Organization


class PhoneNumber(Base):
    __tablename__ = "phone_numbers"

    number: Mapped[str] = mapped_column(String(30), nullable=False)

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False
    )
    organization: Mapped["Organization"] = relationship(back_populates="phone_numbers")

    def __repr__(self):
        return f"<PhoneNumber(number='{self.number}')>"
