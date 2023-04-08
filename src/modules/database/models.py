"""Models for Beanie."""
from beanie import Document, PydanticObjectId
from enum import Enum
# from typing import List
from pydantic import BaseModel, Field
from datetime import datetime


class Achievement(BaseModel):
    """Achievement model for Beanie."""

    name: str
    kind: int  # Achievement type for frontend
    points: int


# Beanie enum for access levels
class CustomListingKind(str, Enum):
    """Custom listing kinds."""

    FEDERAL_44 = "federal_44"


class User(Document):
    """User model for Beanie."""

    email: str
    password_hash: str
    first_name: str
    last_name: str
    phone_number: int
    country: str | None = None
    city: str | None = None
    company_name: str | None = None
    company_inn: int | None = None


class UserAchievements(Document):
    """User achievements model for Beanie."""

    userId: PydanticObjectId
    achievement: Achievement
    ts: datetime = Field(default_factory=datetime.now)


class CustomListing(Document):
    """Custom listings model for Beanie."""

    trackingId: int
    lot: int
    kind: CustomListingKind
    name: str
    companyInn: int
    basePrice: float
    tsEnd: datetime
    tsBegin: datetime = Field(default_factory=datetime.now)
    winnerInn: int | None = None


class CustomListingBid(Document):
    """Custom listing bids model for Beanie."""

    listingTrackingId: int
    listingLot: int
    bidderInn: int
    bidPrice: int
    ts: datetime = Field(default_factory=datetime.now)
