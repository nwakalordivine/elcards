from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from elcards_backend.db import engine, get_db
from sqlalchemy import text


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup the server.
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    print("Database -> reachable")

    yield

    # closeup the server.
    await engine.dispose()



app = FastAPI(title="Elcards backend")


