"""Authentication routes for FastAPI."""
from os import getenv
from typing import Optional, Annotated
from datetime import timedelta
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from modules.database.db import add_user, is_user, \
    elevate_privileges, is_admin
# get_user, get_password_hash
# from modules.database.db import is_company_accessible, get_user_company, \
#     set_user_company_inn, set_user_company_name
# from modules.database.models import User  # , Company
from modules.fastapi_utils import Token, PostRequestResponseModel, \
    UserModel
# , TokenData
from routers.tools import gen_password_hash, authenticate_user, \
    create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, \
    get_current_user


router = APIRouter()


@router.post("/signup", response_model=Token)
async def signup_and_get_access_token(
    email: str,
    password: str,
    name: str,
    surname: str,
    phone_number: int,
    country: Optional[str] = None,
    city: Optional[str] = None
):
    """
    Sign up a new user and return an access token.

    :param user: The user information to sign up.
    :param password: The user's password.
    :return: A dictionary containing the access token and token type.
    """
    # Check if the user already exists
    existing_user = await is_user(email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Create a new user
    hashed_password = gen_password_hash(password)
    await add_user(email, hashed_password, name,
                   surname, phone_number, country, city)

    # Generate and return access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "Bearer"}


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """Provide user with a JWT token on successful authentication."""
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token/json", response_model=Token)
async def login_for_access_token_json(
    user_credentials: dict
):
    """Provide user with a JWT token on successful authentication."""
    user = await authenticate_user(user_credentials['username'],
                                   user_credentials['password'])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/admin/auth", response_model=PostRequestResponseModel)
async def elevate_to_admin(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    password: str
):
    """Elevate user's privileges to administrative.

    If an incorrect password had been supplied, \
return status HTTP 401 UNAUTHORIZED
    """
    if password != getenv("ADMIN_PANEL_PASSWD", ""):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password supplied",
            headers={"WWW-Authenticate": "Bearer"},
        )
    await elevate_privileges(current_user.username)
    return {"message": "Elevated user's privileges to administrative",
            "status": 0}


@router.get("/admin")
async def am_i_admin(
    current_user: Annotated[UserModel, Depends(get_current_user)]
):
    """Check whether the user is an administrator or not."""
    admin: bool = await is_admin(current_user.username)
    return {"is_admin": admin}
