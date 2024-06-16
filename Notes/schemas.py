from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class BaseResponseModel(BaseModel):
    message: str
    status: int

class NotesRequestSchema(BaseModel):
    title: str
    description: str
    color: str
    reminder: Optional[datetime]

class NotesCreationSchema(BaseModel):
    id: int
    title: str
    description: str
    color: str
    reminder: Optional[datetime]
    is_archive: Optional[bool] = False
    is_trash: Optional[bool] = False
    user_id: int

    class Config:
        from_attributes = True

class NotesResponseSchema(BaseResponseModel):
    data: NotesCreationSchema

class NotesResponseModel(BaseResponseModel):
    data: List[NotesCreationSchema]

class LabelSchema(BaseModel):
    label_name: str

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

class NotesLabelSchema(BaseModel):
    id: int
    title: str
    description: str
    color: str
    reminder: Optional[datetime]
    is_archive: bool
    is_trash: bool
    user_id: int
    labels: List[LabelSchema] = []

class NotesLabelResponseSchema(BaseResponseModel):
    data: List[NotesLabelSchema]
