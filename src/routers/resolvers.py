"""Resolve values into different values."""
from typing import Annotated  # , Optional
from fastapi import Depends, APIRouter, HTTPException, status

from modules.database.db import get_company_name_by_inn
# from modules.database.models import User  # , Company
from modules.fastapi_utils import UserModel  # , Token, TokenData
from .tools import get_current_user


router = APIRouter()


@router.get("/resolve/company/by-inn")
async def resolve_company_name_by_inn(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    inn: int
):
    """Resolve company name by its INN.

    If none was provided, return None.
    """
    try:
        name = await get_company_name_by_inn(inn)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company is not present in the database",
        )
    return {"name": name}


@router.get("/")
async def root():
    """Root service function."""
    return {"message": "Hello World"}
