"""SQLAlchemy database management."""

from typing import Optional
from .models import User  # , UserAchievements, CustomListing, CustomListingBid
# from .models import Achievement
# from .models import CustomListingKind
from motor.motor_asyncio import AsyncIOMotorClient
# from pydantic import BaseModel
from beanie import init_beanie  # Document, Indexed,


async def init_db(mongodb_user: str,
                  mongodb_pass: str,
                  mongodb_host: str,
                  mongodb_port: str):
    """Initialize the database manager.

    Pass MongoDB Credentials to initialize this manager.
    """
    client = AsyncIOMotorClient(f"mongodb://{mongodb_user}:\
{mongodb_pass}@{mongodb_host}:{mongodb_port}")
    await init_beanie(database=client.rlt_hack,
                      document_models=[User])  # type: ignore


async def is_user(user_email: str) -> bool:
    """Check if the user exists in the database."""
    return await User.find_one(User.email == user_email) is not None


async def is_company(company_inn: int) -> bool:
    """Check if the company exists in the database."""
    return await User.find_one(company_inn == company_inn) is not None


async def is_company_accessible(user_email: str, company_inn: int) -> bool:
    """Check if the company INN is free or belongs to the user."""
    owner = await User.find_one({"company_inn": company_inn})
    if owner is None:
        return True
    if owner.email == user_email:
        return True
    return False


async def is_company_owner(user_email: str, company_inn: int) -> bool:
    """Check if the user owns the company INN."""
    return await User.find_one(User.email == user_email,
                               User.company_inn == company_inn) is not None


async def add_user(email: str,
                   password_hash: str,
                   name: str,
                   surname: str,
                   phone_number: int,
                   country: Optional[str],
                   city: Optional[str]):
    """Add a user to the database."""
    user = User(email=email,
                password_hash=password_hash,
                first_name=name,
                last_name=surname,
                phone_number=phone_number,
                country=country,
                city=city,
                company_inn=None,
                company_name=None)
    await User.insert_one(user)


async def get_user(user_email: str) -> User | None:
    """Get the user from the database."""
    user = await User.find_one(User.email == user_email)
    return user


async def get_password_hash(user_email: str) -> str:
    """Get password hash stored in the database."""
    user = await User.find_one(User.email == user_email)
    assert user is not None
    return user.password_hash


async def update_user_password(user_email: str, password_hash: str):
    """Update the user password in the database."""
    await (User.find_one(User.email == user_email)
           .set({User.password_hash: password_hash}))


async def update_user_email(user_email: str, new_email: str):
    """Update the user's email in the database."""
    await (User.find_one(User.email == user_email)
           .set({User.email: new_email}))


async def update_user_first_name(user_email: str, name: str):
    """Update the user's name in the database."""
    await (User.find_one(User.email == user_email)
           .set({User.first_name: name}))


async def update_user_last_name(user_email: str, surname: str):
    """Update the user's surname in the database."""
    await (User.find_one(User.email == user_email)
           .set({User.last_name: surname}))


async def update_user_phone_number(user_email: str, phone_number: int):
    """Update the user's phone number in the database."""
    await (User.find_one(User.email == user_email)
           .set({User.phone_number: phone_number}))  # type: ignore


async def update_user_country(user_email: str, country: str | None):
    """Update the user's country in the database."""
    await (User.find_one(User.email == user_email)
           .set({User.country: country}))  # type: ignore


async def update_user_city(user_email: str, city: str | None):
    """Update the user's city in the database."""
    await (User.find_one(User.email == user_email)
           .set({User.city: city}))  # type: ignore


async def set_user_company_name(user_email: str, company_name: str | None):
    """Set user's company name in the database."""
    await (User.find_one(User.email == user_email)
           .set({User.company_name: company_name}))  # type: ignore


async def set_user_company_inn(user_email: str, company_inn: int | None):
    """Set user's company INN in the database."""
    await (User.find_one(User.email == user_email)
           .set({User.company_inn: company_inn}))  # type: ignore


async def get_user_company(user_email: str) -> dict:
    """Get the user companies from the database."""
    user = await User.find_one(User.email == user_email)
    assert user is not None
    return {"company_name": user.company_name,
            "company_inn": user.company_inn}


# async def add_company_listing(user_email: str, listi):
