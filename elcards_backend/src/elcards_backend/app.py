from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from elcards_backend.db import engine, get_db
from sqlalchemy import text, select
from elcards_backend.schemas import RegisterUser, LoginUser, SignUpResponse, ForgotPassword, ResponseReset, ResetPassword
from elcards_backend.models import User
from pwdlib import PasswordHash
from elcards_backend.settings import settings
from elcards_backend.utilities.utils import send_email, get_random_code, get_hash, create_access_token
from elcards_backend.utilities.redis_config import set_redis, redis


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
        email=new_user.email.lower(),
        password_hash=hasher.hash(new_user.password)   
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Creating JWT token with user_id payload.
    response: SignUpResponse = {
        "user": {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "status": user.status
        },
        "token": {
            "access_token": create_access_token(str(user.id)),
            "token_type": "bearer"
        }
    }

    # returns users data and the jwt token to the client.
    return response

    
@app.post("/login")
async def login(
    login_user: LoginUser,
    session: AsyncSession = Depends(get_db)
) -> SignUpResponse:
    db = await session.execute(select(User).where(User.email == login_user.email.lower()))
    user = db.scalar_one_or_none()

    # Checks if user exsistes in the database.
    if user is None:
        raise HTTPException(status_code=404, detail=f"user with email: '{login_user.email}' does not exist.")

    if not hasher.verify(login_user.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.") 

    # Login user return 
    return {
        "user": {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "status": user.status
        },
        "token": {
            "access_token": create_access_token(str(user.id)),
            "token_type": "bearer"
        } 
    }


@app.post("/forgot-password")
async def forgot_password(
    background_task: BackgroundTasks,
    user_email: ForgotPassword,
    session: AsyncSession = Depends(get_db),
) -> ResponseReset:

    attempts = await redis.incr(f"reset_attempt:{user_email.email.lower()}")
    response = ResponseReset(message=f"a {settings.auth_reset_code_lenth}-digit code has been sent to your email if you have an active account.")

    
    if attempts == 1:
        await redis.expire(f"reset_attempt:{user_email.email.lower()}", settings.ratelimit_hour * 3600)

    if attempts > settings.reset_max_attempts:
        return response

    result = await session.execute(select(User).where(User.email == user_email.email.lower()))

    user = result.scalar_one_or_none()

    if user is None:
        return response

    
    # Get otp code.
    otp_code = get_random_code(length=settings.auth_reset_code_lenth)

    # Store in radis
    await set_redis(value=get_hash(otp_code), seconds=(settings.reset_code_timer * 60), key=f"reset:{user.id}")

    # send mail using background tasks
    background_task.add_task(
        send_email, 
        user.email.lower(),
        "Elcards: reset password", 
        otp_code
        )

    return response



@app.post("/reset-password")
async def reset_password(
    request: ResetPassword,
    session: AsyncSession = Depends(get_db)
) -> SignUpResponse:
    
    result = await session.execute(select(User).where(User.email == request.email.lower()))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=400, detail="invalid request: user does not exist.")

    attempts = await redis.incr(f"failed_attmpt:{user.id}")
    if attempts == 1:
        await redis.expire(f"failed_attempt:{user.id}")

    if attempts > settings.change_password_timer:
        await redis.delete(f"reset:{user.id}")
        raise HTTPException(status_code=400, detail="Invalid or expired code.")
    
    redis_value = await redis.get(f"reset:{user.id}")

    if redis_value != get_hash(request.otp_code):
        raise HTTPException(status_code=400, detail="invalid otp. ensure otp is not expired.")

    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="password mismatch, new password and confirm password must match.")

    await redis.delete(f"reset:{user.id}")
    user.password_hash = hasher.hash(request.new_password)

    await session.commit()
    await session.refresh(user)


    response: SignUpResponse = {
        "user": {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "status": user.status,
        },
        "token": {
            "access_token": create_access_token(str(user.id)),
            "token_type": "bearer"
        }
    }
    return response