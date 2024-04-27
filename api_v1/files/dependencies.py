from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper, File

from . import crud


async def file_by_hash(
    file_hash: str,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> File:
    product = await crud.get_file(session=session, file_hash=file_hash)
    if product is not None:
        return product

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"File {file_hash} not found!",
    )
