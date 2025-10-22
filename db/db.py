from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from db.base import Base
from db.seed_data import fill_tables_with_data
from config import settings


class DatabaseHelper:
    def __init__(
        self,
        url: str,
        echo: bool = False,
    ):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session

    async def create_tables(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def fill_tables(self) -> None:
        async with self.session_factory() as session:
            await fill_tables_with_data(session=session)


db_helper = DatabaseHelper(
    url=settings.db_url,
    echo=True,
)
