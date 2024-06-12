from fastapi import FastAPI, Depends, HTTPException, Security, Request
from .models import Base, Notes, Labels, get_db_session
from .schemas import BaseResponseModel, NotesCreationSchema, NotesResponseSchema, NotesResponseModel, LabelsCreationSchema, LabelsResponseSchema, LabelsResponse
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
        is_archive = note.is_archive,
        is_trash = note.is_trash,
        user_id= request.state.user_id
    )
    if not new_note:
        raise HTTPException(detail="error")
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return {"message": "Note Created Successfully", "status": 200, "data": new_note}

@app.get('/notes/', response_model=NotesResponseModel)
def get_notes(request: Request, db: Session = Depends(get_db_session)):
    notes = db.query(Notes).filter(Notes.user_id == request.state.user_id).all()
    if not notes:
        raise HTTPException(status_code=404, detail="No notes found")
    return {"message": "Notes Retrieved Successfully", "status": 200, "data": notes}

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


@app.patch("/notes/{note_id}/archive", response_model = NotesResponseSchema)
def archive_note(request: Request, note_id: int, archive: bool, db: Session = Depends(get_db_session)):
    note = db.query(Notes).filter(Notes.id == note_id, Notes.user_id == request.state.user_id).first()
    if not note:
        raise HTTPException(detail = "Note Not Found", status_code = 404)
    note.is_archive = archive
    db.commit()
    db.refresh(note)
    status = "Archived" if archive else "Unarchived"
    return {"message": f"Note {status} Successfully", "status": 200, "data": note}

@app.patch("/notes/{note_id}/trash", response_model = NotesResponseSchema)
def trash_note(request: Request, note_id: int, trash: bool, db: Session = Depends(get_db_session)):
    note = db.query(Notes).filter(Notes.id == note_id, Notes.user_id == request.state.user_id).first()
    if not note:
        raise HTTPException(detail = "Note Not Found", status_code = 404)
    note.is_trash = trash
    db.commit()
    db.refresh(note)
    status = "Trashed" if trash else "Present"
    return {"message": f"Note {status} Successfully", "status": 200, "data": note}

@app.get('/notes/getArchive', response_model= NotesResponseModel)
def get_archive_notes(request: Request, db: Session = Depends(get_db_session)):
    notes = db.query(Notes).filter(Notes.user_id == request.state.user_id, Notes.is_archive == True, Notes.is_trash == False).all()
    if not notes:
        raise HTTPException(status_code=404, detail="No notes found")
    return {"message": "Notes Archived Successfully", "status": 200, "data": notes}

@app.get('/notes/getTrash', response_model=NotesResponseModel)
def get_trash_notes(request: Request, db: Session = Depends(get_db_session)):
    notes = db.query(Notes).filter(Notes.user_id == request.state.user_id, Notes.is_trash == True).all()
    if not notes:
        raise HTTPException(status_code=404, detail="No notes found")
    return {"message": "Notes Deleted Successfully", "status": 200, "data": notes}


@app.post('/labelcreate', response_model=LabelsResponseSchema)
def add_label(label: LabelsCreationSchema, request: Request, db: Session = Depends(get_db_session)):
    new_label = Labels(
        label_name = label.label_name,
        user_id = request.state.user_id
    )
    if not new_label:
        raise HTTPException(detail="error")
    db.add(new_label)
    db.commit()
    db.refresh(new_label)
    return {"message": "Label Created Successfully", "status": 200, "data": label}

@app.get('/labels/', response_model=LabelsResponse)
def get_labels(request: Request, db: Session = Depends(get_db_session)):
    label = db.query(Labels).filter(Labels.user_id == request.state.user_id).all()
    if not label:
        raise HTTPException(status_code=404, detail="No notes found")
    return {"message": "Labels Retrieved Successfully", "status": 200, "data": label}

@app.put('/labels/{label_id}', response_model=LabelsResponseSchema)
def update_note(request: Request, label_id: int, label_payload: LabelsCreationSchema, db: Session = Depends(get_db_session)):
    label = db.query(Labels).filter(Labels.user_id == request.state.user_id, Labels.id == label_id).first()
    if not label:
        raise HTTPException(status_code=404, detail="Note not found")
    
    label.label_name = label_payload.label_name
    db.commit()
    db.refresh(label)
    return {"message": "Label Updated Successfully", "status": 200, "data":  label}

@app.delete('/labels/{label_id}', response_model=BaseResponseModel)
def delete_note(request: Request, label_id: int, db: Session = Depends(get_db_session)):
    label = db.query(Labels).filter(Labels.id == label_id, Labels.user_id == request.state.user_id).first()
    if not label:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(label)
    db.commit()
    return {"message": "Label deleted successully", "status": 200}