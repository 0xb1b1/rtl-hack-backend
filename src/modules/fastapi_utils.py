"""FastAPI helper utils and classes."""
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


class UserInDB(UserModel):
    """Placeholder TODO: replace."""

    hashed_password: str
