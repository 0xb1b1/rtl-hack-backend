"""Resolve values into different values."""
from typing import Annotated, Optional
from fastapi import Depends, APIRouter, HTTPException, status
import random

from modules.database.db import is_admin, get_daily_statistics, \
    get_monthly_statistics, get_yearly_statistics, get_all_scripts
# from modules.database.models import User  # , Company
from modules.fastapi_utils import UserModel  # , Token, TokenData
from .tools import get_current_user


router = APIRouter()


@router.get("/stats/daily")
async def statistics_daily_read(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    pid: Optional[int] = None
):
    """Get daily statistics (admin-only)."""
    if not await is_admin(current_user.username):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough rights to visit this page",
        )
    if pid is None:
        return (await get_daily_statistics())[0]  # type: ignore
    return (await get_daily_statistics())[pid]  # type: ignore


@router.get("/stats/monthly")
async def statistics_monthly_read(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    pid: Optional[int] = None
):
    """Get monthly statistics (admin-only)."""
    if not await is_admin(current_user.username):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough rights to visit this page",
        )
    if pid is None:
        return (await get_monthly_statistics())[0]  # type: ignore
    return (await get_monthly_statistics())[pid]  # type: ignore


@router.get("/stats/yearly")
async def statistics_yearly_read(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    pid: Optional[int] = None
):
    """Get yearly statistics (admin-only)."""
    if not await is_admin(current_user.username):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough rights to visit this page",
        )
    if pid is None:
        return (await get_yearly_statistics())[0]  # type: ignore
    return (await get_yearly_statistics())[pid]  # type: ignore


# region Admin
@router.get("/admin/scripts")
async def admin_scripts_read(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    limit: Optional[int] = None
):
    """Get all scripts (admin-only)."""
    if not await is_admin(current_user.username):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough rights to visit this page",
        )
    scripts = await get_all_scripts()
    if limit:
        if len(scripts) > limit:
            scripts = scripts[:limit]
    return scripts


@router.get("/admin/scripts/by-metric")
async def admin_scripts_by_metric_read(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    metric: Optional[str] = None,
    limit: Optional[int] = None
):
    """Get all scripts (admin-only)."""
    if not await is_admin(current_user.username):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough rights to visit this page",
        )
    scripts = await get_all_scripts()
    return random.sample(scripts, 3)

# @router.
# endregion
