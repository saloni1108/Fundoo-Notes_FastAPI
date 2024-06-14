from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

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

class NotesResponseModel(BaseResponseModel):
    data: List[NotesCreationSchema]

class LabelsCreationSchema(BaseModel):
    id: int
    label_name: str
    user_id: int

class LabelsResponseSchema(BaseResponseModel):
    data: LabelsCreationSchema

class LabelsResponse(BaseResponseModel):
    data: List[LabelsCreationSchema]

class NoteLabelResponseSchema(BaseModel):
    note_id: int
    label_id: int