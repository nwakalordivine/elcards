from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from elcards_backend.db import engine, get_db
from sqlalchemy import text, select
from elcards_backend.schemas import RegisterUser, LoginUser, SignUpResponse, ResetPassword
from elcards_backend.models import User
from pwdlib import PasswordHash
import jwt
from elcards_backend.settings import settings
from elcards_backend.utils import send_email


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup the server.
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    print("Database -> reachable")

    yield

    # closeup the server.
    await engine.dispose()

hasher = PasswordHash.recommended()

app = FastAPI(title="Elcards backend")

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to Elcards"}


@app.post("/register")
async def register(
        new_user: RegisterUser, 
        session: AsyncSession = Depends(get_db)
    ) -> SignUpResponse:

    # Gets all users
    db = await session.execute(select(User))
    all_users = db.scalars().all()

    # Checks if a different user has same email and/or username.
    for users in all_users:
        if new_user.username == users.username:
            raise HTTPException(status_code=400, detail=f"username: '{new_user.username}' is unavailable.")
        if new_user.email == users.email:
            raise HTTPException(status_code=400, detail="user with this email already exists")

    # Adds the user (registers the user).
    user = User(
        username=new_user.username,
        email=new_user.email,
        password_hash=hasher.hash(new_user.password)   
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Creating JWT token with user_id payload.
    payload = {"user_id": str(user.id)}
    token = jwt.encode(payload, settings.secret, settings.algorithm)

    # returns users data and the jwt token to the client.
    return{
        "user": {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "status": user.status
        },
        "token": {
            "access_token": token,
            "token_type": "bearer"
        }
    }

    
@app.post("/login")
async def login(
    login_user: LoginUser,
    session: AsyncSession = Depends(get_db)
) -> SignUpResponse:
    db = await session.execute(select(User).where(User.email == login_user.email))
    user = db.scalars().all()

    # Checks if user exsistes in the database.
    if not user:
        raise HTTPException(status_code=404, detail=f"user with email: '{login_user.email}' does not exist.")

    if not hasher.verify(login_user.password, user[0].password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.") 

    # Create jwt token for user.
    payload = {"user_id": str(user[0].id)}
    token = jwt.encode(payload, settings.secret, settings.algorithm)

    # Login user return 
    return {
        "user": {
            "id": str(user[0].id),
            "username": user[0].username,
            "email": user[0].email,
            "status": user[0].status
        },
        "token": {
            "access_token": token,
            "token_type": "bearer"
        } 
    }


@app.post("/reset-password")
async def reset_password(
    user_email: ResetPassword,
    session: AsyncSession = Depends(get_db)
):
    db = session.execute(select(User).where(User.email == user_email.email))
    if not db:
        pass

     