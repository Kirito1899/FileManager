from pydantic import BaseModel


class FileBase(BaseModel):
    name: str


class FileResponse(BaseModel):
    hash: str
