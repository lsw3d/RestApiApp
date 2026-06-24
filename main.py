from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn

from fastapi import FastAPI

from db import db_helper
from app import router as app_router
from app.terrain_router import router as terrain_router
from terrain.dem_loader import load_dem


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await db_helper.fill_tables()
    app.state.dem = load_dem()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(app_router)
app.include_router(terrain_router, prefix="/terrain", tags=["terrain"])


if __name__ == "__main__":
    uvicorn.run("main:app")
