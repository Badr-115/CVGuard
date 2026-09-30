from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ...core.security import create_access_token, hash_password, verify_password
from ...db import get_db
from ...dependencies import current_user
from ...models import Organization, User
from ...schemas import LoginIn, RegisterIn, TokenOut

router = APIRouter()


@router.post("/register", response_model=TokenOut, status_code=201)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    email = str(payload.email).lower()
    org = Organization(name=payload.organization_name)
    db.add(org)
    db.flush()
    user = User(
        organization_id=org.id,
        email=email,
        password_hash=hash_password(payload.password),
        role="OWNER",
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Unable to create the account with these details") from exc
    db.refresh(user)
    return {"access_token": create_access_token(str(user.id))}


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == str(payload.email).lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"access_token": create_access_token(str(user.id))}


@router.get("/me")
def me(user=Depends(current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "organization_id": user.organization_id,
    }
