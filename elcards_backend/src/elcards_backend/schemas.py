from pydantic import BaseModel, Field, EmailStr

class RegisterUser(BaseModel):
    username: str = Field(..., min_length=2, max_length=20)
    email: EmailStr
    password: str


class LoginUser(BaseModel):
    email: EmailStr
    password: str

class UserToken(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    id: str
    username: str
    email: EmailStr

class RegisterResponse(BaseModel):
    user: User
    token: UserToken
