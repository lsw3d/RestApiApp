from sqlalchemy import Table, Column, ForeignKey, Integer
from db.base import Base

# --- Many-to-Many связывающая таблица между Organization и Activity
organization_activity_table = Table(
    "organization_activity",
    Base.metadata,
    Column(
        "organization_id", Integer, ForeignKey("organizations.id"), primary_key=True
    ),
    Column("activity_id", Integer, ForeignKey("activities.id"), primary_key=True),
)
