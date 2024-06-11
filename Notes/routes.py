from fastapi import FastAPI, Depends, HTTPException, Security, Request
from .models import Base, Notes, get_db_session
from .schemas import BaseResponseModel, NotesCreationSchema, NotesResponseSchema
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import APIKeyHeader


app = FastAPI()

@app.post('/notecreate', response_model = NotesResponseSchema)
def add_user(note_payload: NotesCreationSchema, db: Session = Depends(get_db_session)):
    note = Notes(**note_payload.model_dump())
    db.add(note)
    db.commit()
    db.refresh(note)
    return {"message": "Note Created Successfully", "status": 200, "data": note}

@app.get('/notes/{userid}', response_model=List[NotesCreationSchema])
def get_note(request: Request, userid: int, db: Session = Depends(get_db_session)):
    note = db.query(Notes).filter(Notes.user_id == userid).all()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.put('/notes/{userid}', response_model=NotesResponseSchema)
def update_note(userid: int, note_payload: NotesCreationSchema, db: Session = Depends(get_db_session)):
    note = db.query(Notes).filter(Notes.user_id == userid).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note.title = note_payload.title
    note.description = note_payload.description
    db.commit()
    db.refresh(note)
    return {"message": "Note Updated Successfully", "status": 200, "data":  note}

@app.delete('/notes/{note_id}', response_model=BaseResponseModel)
def delete_note(note_id: int, db: Session = Depends(get_db_session)):
    note = db.query(Notes).filter(Notes.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(note)
    db.commit()
    return {"message": "Note deleted successully", "status": 200}
