import hashlib
from pathvalidate import sanitize_filename
from fastapi import UploadFile, HTTPException
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.config import settings
from core.models import File, User

import aiofiles
import aiofiles.os


async def get_files(session: AsyncSession, user: User) -> list[File]:
    stmt = select(File).where(File.user_id == user.id)
    result: Result = await session.execute(stmt)
    products = result.scalars().all()
    return list(products)


async def get_file(session: AsyncSession, file_hash: str) -> File | None:
    stmt = select(File).where(file_hash == File.hash)
    result: Result = await session.execute(stmt)
    file = result.scalar()
    return file


async def upload_file(session: AsyncSession, user: User, cont_file: UploadFile) -> File:
    clear_filename = sanitize_filename(cont_file.filename)
    file_hash = hashlib.sha256(clear_filename.encode()).hexdigest()

    check_file = await get_file(session, file_hash)
    if check_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File already uploaded",
        )

    new_file = File(user_id=user.id, hash=file_hash, name=clear_filename)
    await write_file(file_hash, cont_file)
    session.add(new_file)
    await session.commit()
    return new_file


async def delete_file(
    session: AsyncSession,
    file: File,
    user: User,
) -> None:
    if file.user_id == user.id:
        dir_hash = file.hash[:2]
        await aiofiles.os.remove(f'{settings.dir_save}/{dir_hash}/{file.hash}')
        await session.delete(file)
        await session.commit()


async def write_file(file_hash: str, file: UploadFile):
    dir_hash = file_hash[:2]
    await aiofiles.os.makedirs(f'{settings.dir_save}/{dir_hash}', exist_ok=True, mode=0o755)
    async with aiofiles.open(f'{settings.dir_save}/{dir_hash}/{file_hash}', 'wb') as buffer:
        data = await file.read()
        await buffer.write(data)
