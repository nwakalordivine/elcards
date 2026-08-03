from fastapi import FastAPI, Depends, HTTPException
from elcards_backend.db import create_sync_table
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_sync_table()
    yield


app = FastAPI(title="Elcards Backend", lifespan=lifespan)

@app.get("/")
async def index():
    return {"message": "welcome to Elcards"}