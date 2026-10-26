"""
Dependencies module for SmartSilageAI FastAPI backend.
Extracts authenticated farmer from Authorization header.
Supports a demo mode fallback if no auth token is provided during testing.
"""
from typing import Optional
from fastapi import Header, HTTPException, Depends, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.farmer import Farmer
from backend.services.auth_service import verify_token


def get_current_farmer_optional(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[Farmer]:
    """Returns authenticated farmer or None."""
    if not authorization:
        return None
    token = authorization.replace("Bearer ", "").strip()
    farmer_id = verify_token(token)
    if not farmer_id:
        return None
    return db.query(Farmer).filter(Farmer.id == farmer_id).first()


def get_current_farmer(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Farmer:
    """Enforces authentication. If token missing, raises 401."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.replace("Bearer ", "").strip()
    farmer_id = verify_token(token)
    if not farmer_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired or token is invalid. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer profile not found.")
    return farmer
