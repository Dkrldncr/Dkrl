from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import select

from app.core.db import get_session
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User, UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session=Depends(get_session)) -> User:
    from app.core.security import get_subject_from_token, InvalidTokenError

    try:
        email = get_subject_from_token(token)
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@router.post("/register", response_model=UserRead)
async def register(user_in: UserCreate, session=Depends(get_session)):
    existing = session.exec(select(User).where(User.email == user_in.email)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = User(email=user_in.email, hashed_password=hash_password(user_in.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session=Depends(get_session)):
    user: Optional[User] = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")

    token = create_access_token(subject=user.email)
    return {"access_token": token, "token_type": "bearer"}