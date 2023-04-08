"""Models for Beanie."""
from beanie import Document
from enum import Enum
# from pydantic import Field
from typing import List


# Beanie enum for access levels
class AccessLevel(str, Enum):
    """Access levels for users in companies."""

    # User can view all company's data
    VIEWER = "viewer"
    # User can edit all company's data
    EDITOR = "editor"
    # User can delete all company's data
    OWNER = "owner"


class User(Document):
    """User model for Beanie."""

    # userId: str = Field(None, alias="_id")
    email: str
    password_hash: str
    first_name: str
    last_name: str
    companies: List[dict]  # inn+AccessLevel


class Company(Document):
    """Company model for Beanie."""

    name: str
    inn: int
