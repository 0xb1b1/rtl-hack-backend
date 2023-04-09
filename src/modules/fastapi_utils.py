"""FastAPI helper utils and classes."""
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


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
    is_admin: Optional[bool] = False
    country: Optional[str] = None
    city: Optional[str] = None


class UserEditModel(BaseModel):
    """User data model (editing)."""

    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[int] = None
    is_admin: Optional[bool] = False
    country: Optional[str] = None
    city: Optional[str] = None


class CustomListingModel(BaseModel):
    """Custom Listing model."""

    trackingId: int
    lot: int
    kind: str
    name: str
    companyInn: int
    basePrice: float
    isActive: bool
    dynamic: int
    tsEnd: datetime
    tsBegin: datetime
    winnerInn: int | None = None


class CustomListingCreateModel(BaseModel):
    """Custom Listing creation model."""

    trackingId: int
    lot: int
    kind: str
    name: str
    description: str
    basePrice: float
    tsEnd: datetime


class PostRequestResponseModel(BaseModel):
    """Post request response model."""

    message: str
    status: int
