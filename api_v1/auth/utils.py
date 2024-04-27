from passlib.hash import sha256_crypt

from sqlalchemy.ext.asyncio import AsyncSession
from core.models import User


def hash_password(
    password: str,
) -> str:
    return sha256_crypt.using(rounds=5000).hash(password)


def verify_password(
    password: str,
    hashed: str
) -> bool:
    return sha256_crypt.verify(password, hashed)