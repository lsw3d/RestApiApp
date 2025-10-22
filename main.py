from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn

from fastapi import FastAPI

from db import db_helper
from app import router as app_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await db_helper.fill_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(app_router)


if __name__ == "__main__":
    uvicorn.run("main:app")
