"""
Pydantic Schemas for Farmer Authentication & Profiles
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class FarmerRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="Ramesh Patel")
    mobile: str = Field(..., min_length=10, max_length=15, example="9876543210")
    email: Optional[str] = Field(None, max_length=120, example="ramesh@example.com")
    location: Optional[str] = Field(None, max_length=150, example="Anand, Gujarat")
    password: str = Field(..., min_length=4, max_length=64, example="farmer123")


class FarmerLogin(BaseModel):
    mobile: str = Field(..., example="9876543210")
    password: str = Field(..., example="farmer123")


class FarmerOut(BaseModel):
    id: int
    name: str
    mobile: str
    email: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    farmer: FarmerOut
