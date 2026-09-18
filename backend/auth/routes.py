import uuid
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Merchant, User

from .security import (
    hash_password,
    verify_password,
    create_access_token
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


class RegisterRequest(BaseModel):
    email: str
    password: str
    business_name: str


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    email = request.email.lower().strip()
    business_name = request.business_name.strip()

    if not email:
        raise HTTPException(
            status_code=400,
            detail="Email is required"
        )

    if len(request.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 8 characters"
        )

    if not business_name:
        raise HTTPException(
            status_code=400,
            detail="Business name is required"
        )

    existing_user = db.query(User).filter(
        User.email == email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    merchant = Merchant(
        merchant_id=f"M{uuid.uuid4().hex[:10].upper()}",
        business_name=business_name
    )

    db.add(merchant)
    db.flush()

    user = User(
        email=email,
        password_hash=hash_password(request.password),
        merchant_id=merchant.id
    )

    db.add(user)
    db.commit()

    db.refresh(merchant)
    db.refresh(user)

    return {
        "message": "Registration successful",
        "merchant_id": merchant.merchant_id,
        "business_name": merchant.business_name,
        "email": user.email
    }

@router.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    email = request.email.lower().strip()

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        request.password,
        user.password_hash
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    merchant = (
        db.query(Merchant)
        .filter(
            Merchant.id == user.merchant_id
        )
        .first()
    )

    token = create_access_token({
        "sub": str(user.id),
        "merchant_id": merchant.merchant_id,
        "email": user.email
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "merchant_id": merchant.merchant_id,
        "business_name": merchant.business_name,
        "email": user.email
    }