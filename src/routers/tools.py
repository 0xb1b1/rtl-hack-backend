"""Tools for FastAPI Server."""
from os import getenv
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Annotated  # , Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
# , OAuth2PasswordRequestForm
from jose import JWTError, jwt

from modules.database.db import get_user, get_password_hash
from modules.fastapi_utils import TokenData, UserModel
from modules.database.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# `openssl rand -hex 32``
SECRET_KEY = getenv("JWT_SECRET", "")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def gen_password_hash(password: str) -> str:
    """Get hash from supplied string."""
    return pwd_context.hash(password)


async def authenticate_user(email: str, password: str):
    """Return User DB object on successful authentication."""
    user = await get_user(email)
    if not user:
        return None
    if not pwd_context.verify(password, await get_password_hash(email)):
        return None
    return user


def create_access_token(data: dict,
                        expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=6)
    to_encode.update(**{"exp": expire})
    encoded_jwt: str = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)]) -> UserModel:
    """Get user's information from their JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")  # type: ignore
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    assert isinstance(token_data.username, str)  # nosec
    user = await get_user(username)
    if user is None:
        raise credentials_exception
    assert user is not None  # nosec
    user_model = await convert_user(user)
    return user_model


async def convert_user(user: User) -> UserModel:
    """Convert User DB model to Pydantic UserModel."""
    return UserModel(username=str(user.email),
                     first_name=str(user.first_name),
                     last_name=str(user.last_name),
                     phone_number=int(user.phone_number),
                     country=user.country,
                     city=user.city)
