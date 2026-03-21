from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, TokenResponse
from app.security import create_access_token, verify_password

router = APIRouter(prefix="/auth")


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Annotated[Session, Depends(get_db)]) -> TokenResponse:
    uname = body.username.strip().lower()
    user = db.scalars(select(User).where(func.lower(User.username) == uname)).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(str(user.id), extra_claims={"role": user.role.value})
    return TokenResponse(access_token=token)
