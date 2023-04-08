"""SQLAlchemy database management."""

# region Dependencies
# from datetime import date, datetime, timedelta
# from time import sleep
# from sqlalchemy.orm import sessionmaker
# from .models import Base, User
# from sqlalchemy import create_engine
# # from typing import List, Union, Tuple
# from sqlalchemy.exc import OperationalError as sqlalchemyOpError
# from psycopg2 import OperationalError as psycopg2OpError
# endregion
from .models import User, Company
from .models import AccessLevel
from motor.motor_asyncio import AsyncIOMotorClient
# from pydantic import BaseModel
from typing import List, Dict

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
                      document_models=[User,
                                       Company])  # type: ignore


async def is_user(user_email: str) -> bool:
    """Check if the user exists in the database."""
    return await User.find_one(User.email == user_email) is not None


async def is_company(company_inn: int) -> bool:
    """Check if the company exists in the database."""
    return await Company.find_one(Company.inn == company_inn) is not None


async def add_user(email: str,
                   password_hash: str,
                   name: str,
                   surname: str):
    """Add a user to the database."""
    user = User(email=email,
                password_hash=password_hash,
                first_name=name,
                last_name=surname,
                companies=[])
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
    """Update the user email in the database."""
    await (User.find_one(User.email == user_email)
           .set({User.email: new_email}))


async def update_user_first_name(user_email: str, name: str):
    """Update the user name in the database."""
    await (User.find_one(User.email == user_email)
           .set({User.first_name: name}))


async def update_user_last_name(user_email: str, surname: str):
    """Update the user surname in the database."""
    await (User.find_one(User.email == user_email)
           .set({User.last_name: surname}))


async def get_user_companies(user_email: str) -> List[Dict[int, AccessLevel]]:
    """Get the user companies from the database."""
    user = await User.find_one(User.email == user_email)
    assert user is not None
    # Add company names to all return dicts
    companies = user.companies
    for company in companies:
        company["name"] = ((await Company.find_one(Company.inn ==
                                                   company["inn"]))
                           .name)  # type: ignore
    return companies


async def add_user_company(user_email: str,
                           company_name: str,
                           company_inn: int):
    """Create a new company and assign the user as its AccessType.OWNER."""
    user = await User.find_one(User.email == user_email)
    assert user is not None
    companies = user.companies
    await Company.insert_one(Company(name=company_name, inn=company_inn))
    companies.append({"inn": company_inn,
                      "access": AccessLevel.OWNER})
    await user.set({User.companies: companies})  # type: ignore


async def del_user_company(user_email: str, company_inn: int):
    """Delete the user company from the database."""
    user = await User.find_one(User.email == user_email)
    assert user is not None
    companies = user.companies
    new_companies: List[dict] = []
    for company in companies:
        if company["inn"] != company_inn:
            new_companies.append(company)
    await (User.find_one(User.email == user_email)
           .set({User.companies: new_companies}))  # type: ignore
