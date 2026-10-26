"""
Authentication Router for SmartSilageAI (SIH26111)
Handles farmer registration, login, and profile lookup.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.farmer import Farmer
from backend.schemas.farmer import FarmerRegister, FarmerLogin, FarmerOut, TokenResponse
from backend.services.auth_service import hash_password, verify_password, create_access_token
from backend.dependencies import get_current_farmer

router = APIRouter(prefix="/api", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_farmer(payload: FarmerRegister, db: Session = Depends(get_db)):
    """
    Registers a new dairy farmer or field officer.
    """
    existing = db.query(Farmer).filter(Farmer.mobile == payload.mobile.strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mobile number {payload.mobile} is already registered. Please log in.",
        )
    
    farmer = Farmer(
        name=payload.name.strip(),
        mobile=payload.mobile.strip(),
        email=payload.email.strip() if payload.email else None,
        location=payload.location.strip() if payload.location else None,
        password_hash=hash_password(payload.password),
    )
    db.add(farmer)
    db.commit()
    db.refresh(farmer)
    
    token = create_access_token(farmer.id, farmer.mobile)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        farmer=FarmerOut.model_validate(farmer)
    )


@router.post("/login", response_model=TokenResponse)
def login_farmer(payload: FarmerLogin, db: Session = Depends(get_db)):
    """
    Farmer / field worker login using mobile number and password.
    """
    farmer = db.query(Farmer).filter(Farmer.mobile == payload.mobile.strip()).first()
    if not farmer or not verify_password(payload.password, farmer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect mobile number or password. For demo, use 9876543210 / farmer123.",
        )
    
    token = create_access_token(farmer.id, farmer.mobile)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        farmer=FarmerOut.model_validate(farmer)
    )


@router.get("/me", response_model=FarmerOut)
def get_current_farmer_profile(farmer: Farmer = Depends(get_current_farmer)):
    """
    Returns current authenticated farmer profile.
    """
    return FarmerOut.model_validate(farmer)
