from pydantic import BaseModel, Field, EmailStr

class RegisterUser(BaseModel):
    username: str = Field(..., min_length=2, max_length=20)
    email: EmailStr
    password: str


class LoginUser(BaseModel):
    email: EmailStr
    password: str