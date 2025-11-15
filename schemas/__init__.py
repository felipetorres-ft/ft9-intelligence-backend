from pydantic import BaseModel, EmailStr
from typing import Optional

# necessário para tratar schemas como package
# Authentication schemas

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None

class LoginRequest(BaseModel):
    email: str
    password: str

__all__ = ["Token", "TokenData", "LoginRequest"]
