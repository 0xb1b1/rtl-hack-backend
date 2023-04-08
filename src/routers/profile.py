"""User/Company profile mutation and view."""
from typing import Annotated  # , Optional
from fastapi import Depends, APIRouter, HTTPException, status

from modules.database.db import is_company_accessible, get_user_company, \
    set_user_company_inn, set_user_company_name, update_user_first_name, \
    update_user_last_name
# from modules.database.models import User  # , Company
from modules.fastapi_utils import UserModel  # , Token, TokenData, UserInDB
from .tools import get_current_user


router = APIRouter()


# region User
@router.get("/user", response_model=UserModel)
async def current_user_read(
    current_user: Annotated[UserModel, Depends(get_current_user)]
):
    """Return user's details."""
    return current_user


@router.get("/user/first_name")
async def current_user_first_name_read(
    current_user: Annotated[UserModel, Depends(get_current_user)],
):
    """Get user's first name."""
    return {"first_name": current_user.first_name,
            "status": 0}


@router.get("/user/last_name")
async def current_user_last_name_read(
    current_user: Annotated[UserModel, Depends(get_current_user)],
):
    """Get user's last name."""
    return {"first_name": current_user.last_name,
            "status": 0}


@router.post("/user/first_name")
async def current_user_first_name_write(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    first_name: str
):
    """Change user's company name."""
    await update_user_first_name(current_user.username, first_name)
    return {"message": "User's first name updated",
            "first_name": first_name,
            "status": 0}


@router.post("/user/last_name")
async def current_user_last_name_write(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    last_name: str
):
    """Change user's company name."""
    await update_user_last_name(current_user.username, last_name)
    return {"message": "User's last name updated",
            "last_name": last_name,
            "status": 0}
# endregion


# region Company
@router.get("/user/company")
async def current_user_company_read(
    current_user: Annotated[UserModel, Depends(get_current_user)]
):
    """Return user's companies."""
    return await get_user_company(current_user.username)


@router.post("/user/company/inn")
async def current_user_company_inn_write(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    company_inn: int | None = None
):
    """Change user's company INN.

    Raise HTTPException if the company INN already exists.
    """
    if company_inn is not None:
        if not await is_company_accessible(current_user.username, company_inn):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company with this INN already exists",
            )
    await set_user_company_inn(current_user.username, company_inn)
    return {"message": "Company INN updated",
            "company_inn": company_inn,
            "status": 0}


@router.post("/user/company/name")
async def current_user_company_name_write(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    company_name: str | None = None
):
    """Change user's company name."""
    await set_user_company_name(current_user.username, company_name)
    return {"message": "Company name updated",
            "company_name": company_name,
            "status": 0}
# endregion
