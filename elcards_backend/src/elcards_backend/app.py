from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from elcards_backend.db import engine, get_db
from sqlalchemy import text, select
from elcards_backend.schemas import RegisterUser, LoginUser, RegisterResponse
from elcards_backend.models import User
from pwdlib import PasswordHash
import jwt
from elcards_backend.settings import settings


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

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to Elcards"}


@app.post("/register")
async def register(
        new_user: RegisterUser, 
        session: AsyncSession = Depends(get_db)
    ) -> RegisterResponse:

    db = await session.execute(select(User))
    all_users = db.scalars().all()

    for users in all_users:
        if new_user.username == users.username:
            raise HTTPException(status_code=400, detail=f"username: '{new_user.username}' is unavailable.")
        if new_user.email == users.email:
            raise HTTPException(status_code=400, detail="user with this email already exists")

    hasher = PasswordHash.recommended()

    user = User(
        username=new_user.username,
        email=new_user.email,
        password_hash=hasher.hash(new_user.password)   
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    payload = {"user_id": str(user.id)}
    token = jwt.encode(payload, settings.secret, settings.algorithm)

    return{
        "user": {
            "id": str(user.id),
            "username": user.username,
            "email": user.email
        },
        "token": {
            "access_token": token,
            "token_type": "bearer"
        }
    }
    
