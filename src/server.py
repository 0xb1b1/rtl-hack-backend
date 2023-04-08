"""Docstring."""
from os import getenv
# from typing import Annotated
from fastapi import FastAPI  # , Depends
from fastapi.security import OAuth2PasswordBearer

from modules.database.db import init_db
# from modules.fastapi_utils import UserModel
# from routers.tools import get_current_user
from routers import auth, profile


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()
app.include_router(auth.router)
app.include_router(profile.router)

# def verify_password(plain_password, hashed_password) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)


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
