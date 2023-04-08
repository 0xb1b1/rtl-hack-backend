"""FastAPI helper utils and classes."""
from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """Authentication token model."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data model."""

    username: str


class UserModel(BaseModel):
    """User data model."""

    username: str
    first_name: str
    last_name: str
    phone_number: int
    country: Optional[str] = None
    city: Optional[str] = None


class UserInDB(UserModel):
    """Placeholder TODO: replace."""

    hashed_password: str
