from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models

from .auth_utils import (
    verify_password,
    create_access_token,
    create_refresh_token,
    SECRET_KEY,
    ALGORITHM
)
from jose import JWTError, jwt
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginSchema(BaseModel):
    username: str
    password: str


class RefreshSchema(BaseModel):
    refresh_token: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🔐 LOGIN
@router.post("/login")
def login(data: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == data.username).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({
        "sub": user.username,
        "role": user.role
    })

    refresh_token = create_refresh_token({
        "sub": user.username,
        "type": "refresh"
    })

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# 🔄 REFRESH TOKEN
@router.post("/refresh")
def refresh_token(data: RefreshSchema):
    token = data.refresh_token

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        username = payload.get("sub")

        new_access = create_access_token({
            "sub": username
        })

        return {"access_token": new_access}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")