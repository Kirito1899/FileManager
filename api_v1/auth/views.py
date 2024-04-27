from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper, User
from .utils import hash_password, verify_password
router = APIRouter(prefix="/demo-auth", tags=["Demo Auth"])

security = HTTPBasic()


@router.get("/basic-auth/")
def demo_basic_auth_credentials(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    return {
        "message": "Hi!",
        "username": credentials.username,
    }


usernames_to_passwords = {
    "admin": hash_password('admin'),
    "john": hash_password("password"),
}
print(usernames_to_passwords)


def get_auth_user_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
) -> str:
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Basic"},
    )
    correct_password = usernames_to_passwords.get(credentials.username)
    if correct_password is None:
        raise unauthed_exc

    # secrets
    if not verify_password(credentials.password, correct_password):
        raise unauthed_exc

    return credentials.username


async def get_current_user(credentials: Annotated[HTTPBasicCredentials, Depends(security)],
                           session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    """ Check auth user
    """
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Basic"},
    )
    # correct_password = usernames_to_passwords.get(credentials.username)
    stmt = select(User).where(User.username == credentials.username)
    user = await session.scalars(stmt)
    user = user.one_or_none()

    if user is None:
        raise unauthed_exc

    # secrets
    if not verify_password(credentials.password, user.password):
        raise unauthed_exc

    return user


@router.get("/login")
def demo_basic_auth_username(
    auth_username: str = Depends(get_current_user),
):
    return {
        "message": f"Hi, {auth_username}!",
        "username": auth_username,
    }
