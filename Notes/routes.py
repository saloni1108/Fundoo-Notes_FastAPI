from fastapi import FastAPI, Depends, HTTPException, Security, Request
from .models import Base, Notes, get_db_session
from .schemas import BaseResponseModel, NotesCreationSchema, NotesResponseSchema
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import APIKeyHeader
from .utils import auth_user


app = FastAPI(dependencies = [Security(APIKeyHeader(name = "Authorization")), Depends(auth_user)])

@app.post('/notecreate', response_model=NotesResponseSchema)
def add_note(note: NotesCreationSchema, request: Request, db: Session = Depends(get_db_session)):
    new_note = Notes(
        title=note.title,
        description=note.description,
        color=note.color,
        user_id= request.state.user_id
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return {"message": "Note Created Successfully", "status": 200, "data": new_note}

@app.get('/notes/', response_model=List[NotesCreationSchema])
def get_notes(request: Request, db: Session = Depends(get_db_session)):
    notes = db.query(Notes).filter(Notes.user_id == request.state.user_id).all()
    if not notes:
        raise HTTPException(status_code=404, detail="No notes found")
    return notes

@app.put('/notes/{note_id}', response_model=NotesResponseSchema)
def update_note(request: Request, note_id: int, note_payload: NotesCreationSchema, db: Session = Depends(get_db_session)):
    note = db.query(Notes).filter(Notes.user_id == request.state.user_id, Notes.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note.title = note_payload.title
    note.description = note_payload.description
    db.commit()
    db.refresh(note)
    return {"message": "Note Updated Successfully", "status": 200, "data":  note}

@app.delete('/notes/{note_id}', response_model=BaseResponseModel)
def delete_note(request: Request, note_id: int, db: Session = Depends(get_db_session)):
    note = db.query(Notes).filter(Notes.id == note_id, Notes.user_id == request.state.user_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(note)
    db.commit()
    return {"message": "Note deleted successully", "status": 200}
