from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BaseResponseModel(BaseModel):
    message: str
    status: int

class NotesCreationSchema(BaseModel):
    id: int
    title: str
    description: str
    color: str
    reminder: Optional[datetime]
    is_archive: Optional[bool] = False
    is_trash: Optional[bool] = False
    user_id: int


class NotesResponseSchema(BaseResponseModel):
    data: NotesCreationSchema