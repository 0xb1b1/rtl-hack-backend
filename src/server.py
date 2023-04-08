"""Docstring."""
from os import getenv
from datetime import datetime, timedelta
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

from modules.database.db import init_db, add_user, is_user, get_user, \
    get_password_hash, get_user_companies
from modules.database.db import is_company, add_user_company
from modules.database.models import User  # , Company
from modules.fastapi_utils import Token, TokenData, UserModel  # , UserInDB

# `openssl rand -hex 32``
SECRET_KEY = getenv("JWT_SECRET", "")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

# def verify_password(plain_password, hashed_password) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)


def gen_password_hash(password: str) -> str:
    """Get hash from supplied string."""
    return pwd_context.hash(password)


async def authenticate_user(email: str, password: str):
    """Return User DB object on successful authentication."""
    user = await get_user(email)
    if not user:
        return None
    if not pwd_context.verify(password, await get_password_hash(email)):
        return None
    return user


def create_access_token(data: dict,
                        expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)]) -> UserModel:
    """Get user's information from their JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")  # type: ignore
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    assert isinstance(token_data.username, str)  # nosec
    user = await get_user(username)
    if user is None:
        raise credentials_exception
    assert user is not None  # nosec
    user_model = await convert_user(user)
    return user_model


async def convert_user(user: User) -> UserModel:
    """Convert User DB model to Pydantic UserModel."""
    return UserModel(username=str(user.email),
                     first_name=str(user.first_name),
                     last_name=str(user.last_name))


@app.on_event("startup")
async def start_db():
    """Start database on FastAPI startup."""
    await init_db(getenv("MONGODB_USER", ""),
                  getenv("MONGODB_PASS", ""),
                  getenv("MONGODB_HOST", ""),
                  getenv("MONGODB_PORT", ""))


@app.get("/")
async def root():
    """Root service function."""
    return {"message": "Hello World"}


@app.post("/signup", response_model=Token)
async def signup_and_get_access_token(
    email: str,
    password: str,
    name: str,
    surname: str
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
    await add_user(email, hashed_password, name, surname)

    # Generate and return access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/token", response_model=Token)
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


@app.get("/user", response_model=UserModel)
async def current_user_read(
    current_user: Annotated[UserModel, Depends(get_current_user)]
):
    """Return user's details."""
    return current_user


@app.get("/user/companies")
async def current_user_companies_read(
    current_user: Annotated[UserModel, Depends(get_current_user)]
):
    """Return user's companies."""
    return await get_user_companies(current_user.username)


@app.post("/user/companies/create")
async def current_user_companies_create(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    company_name: str,
    company_inn: int
):
    """Create a new company and assign current user as AccessType.OWNER.

    Raise HTTPException if the company already exists.
    """
    company = await is_company(company_inn)
    if company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company with this INN already exists",
        )
    await add_user_company(current_user.username, company_name, company_inn)
    return {"message": "Company created"}
