from pydantic import BaseModel, EmailStr, Field
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
    name: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    # Admin user data
    admin_email: EmailStr
    admin_password: str = Field(..., min_length=8)
    admin_full_name: str = Field(..., min_length=3)

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    whatsapp_phone_number: Optional[str] = None

class OrganizationResponse(OrganizationBase):
    id: int
    slug: str

    class Config:
        from_attributes = True  # Updated from orm_mode

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
        from_attributes = True  # Updated from orm_mode

__all__ = ["Token", "TokenData", "LoginRequest", "OrganizationBase", "OrganizationCreate", "OrganizationUpdate", "OrganizationResponse", "UserBase", "UserResponse"]
