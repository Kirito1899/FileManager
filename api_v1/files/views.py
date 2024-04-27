from fastapi import APIRouter, status, Depends, UploadFile, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import db_helper, User, File
from . import crud
from .dependencies import file_by_hash
from .schemas import FileResponse as FileResponseSchema
from ..auth.views import get_current_user

router = APIRouter(tags=["Files"])


@router.get("/", response_model=list[FileResponseSchema])
async def get_files(
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
        user: User = Depends(get_current_user),
):
    files = await crud.get_files(session=session, user=user)
    hashes = [FileResponseSchema(hash=file.hash) for file in files]
    return hashes


@router.post(
    "/",
    response_model=FileResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def upload_file(
        file_in: UploadFile,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
        user: User = Depends(get_current_user),
):
    new_file = await crud.upload_file(session=session, cont_file=file_in, user=user)
    return FileResponseSchema(hash=new_file.hash)


@router.get("/{file_hash}/")
async def get_file(
        file: File = Depends(file_by_hash),
        user: User = Depends(get_current_user),
):
    if file:
        dir_hash = file.hash[:2]
        return FileResponse(path=f'{settings.dir_save}/{dir_hash}/{file.hash}', filename=file.name,
                            media_type='multipart/form-data')
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not Found",
        )


@router.delete("/{file_hash}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
        file: File = Depends(file_by_hash),
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
        user: User = Depends(get_current_user),
) -> None:
    await crud.delete_file(session=session, file=file, user=user)
