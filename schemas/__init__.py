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

# Organization schemas
class OrganizationBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: Optional[str] = None
    cnpj: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(OrganizationBase):
    pass

class Organization(OrganizationBase):
    id: int

    class Config:
        orm_mode = True

class OrganizationResponse(Organization):
    """Alias para OrganizationResponse"""
    pass

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: Optional[str] = None

class UserResponse(UserBase):
    id: int
    organization_id: int
    is_active: bool = True

    class Config:
        orm_mode = True

__all__ = ["Token", "TokenData", "LoginRequest", "OrganizationBase", "OrganizationCreate", "OrganizationUpdate", "Organization", "OrganizationResponse", "UserBase", "UserResponse"]
