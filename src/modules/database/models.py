"""Models for Beanie."""
from beanie import Document, PydanticObjectId
from typing import List
from pydantic import BaseModel, Field
from datetime import datetime


class Achievement(BaseModel):
    """Achievement model for Beanie."""

    name: str
    kind: int  # Achievement type for frontend
    points: int


# # Beanie enum for access levels
# class CustomListingKind(str, Enum):
#     """Custom listing kinds."""

#     FEDERAL_44 = "federal_44"

# # Beanie enum for Script type
# class ScriptKind(str, Enum):
#     """Script kinds."""

#     SUPPLIER = "supplier"
#     CUSTOMER = "customer"
#     ALL = "all"


class User(Document):
    """User model for Beanie."""

    email: str
    passwordHash: str
    firstName: str
    lastName: str
    phoneNumber: int
    isAdmin: bool = False
    country: str | None = None
    city: str | None = None
    companyName: str | None = None
    companyInn: int | None = None


class UserAchievements(Document):
    """User achievements model for Beanie."""

    userId: PydanticObjectId
    achievement: Achievement
    ts: datetime = Field(default_factory=datetime.now)  # type: ignore


class CustomListing(Document):
    """Custom listings model for Beanie."""

    trackingId: int
    lot: int
    kind: str
    name: str
    description: str
    companyInn: int
    basePrice: float
    isActive: bool
    tsEnd: datetime
    dynamic: int
    tsBegin: datetime = Field(default_factory=datetime.now)
    winnerInn: int | None = None


class CustomListingBid(Document):
    """Custom listing bids model for Beanie."""

    listingTrackingId: int
    listingLot: int
    bidderInn: int
    bidPrice: float
    ts: datetime = Field(default_factory=datetime.now)


class StatisticsProto(Document):
    """Statistics prototype model for Beanie."""

    daily: List[List[dict]] | None
    monthly: List[List[dict]] | None
    yearly: List[List[dict]] | None


# region Events
class Metric(Document):
    """Metric model for Beanie."""

    name: str
    history: dict  # {'supplier': [...], 'customer': [...], 'all': [...]}


class TaskGoal(Document):
    """Task goal model for Beanie."""

    name: str
    target: dict  # {"kind": "full-profile", "count": 1}


class Task(Document):
    """Task model for Beanie."""

    name: str
    description: str
    daysToComplete: int
    taskGoals: List[str]  # TaskGoal names
    metrics: List[str]  # ["CRR", "CR", "ROI/ROMI"]


class Script(Document):
    """Script model for Beanie."""

    name: str
    description: str
    tasks: List[str]  # Task names
    metrics: list  # Metric, Weight
    kind: str  # "all" / ...
# endregion
