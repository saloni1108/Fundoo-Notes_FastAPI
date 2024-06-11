from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BaseResponseModel(BaseModel):
    message: str
    status: int

class NotesCreationSchema(BaseModel):
    title: str
    description: str
    color: str
    reminder: Optional[datetime]
    user_id: int


class NotesResponseSchema(BaseResponseModel):
    data: NotesCreationSchema