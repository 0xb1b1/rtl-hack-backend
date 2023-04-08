"""Utilities folder."""
from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    """Return hashed password string."""
    # Use bcrypt algo
    return password_context.hash(password, scheme="bcrypt")


def verify_password(password: str, hashed_pass: str) -> bool:
    """Verify supplied password against its hashed version."""
    return password_context.verify(password, hashed_pass, scheme="bcrypt")
