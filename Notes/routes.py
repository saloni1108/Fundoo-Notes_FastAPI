from fastapi import FastAPI, Depends, HTTPException, Security, Request
from .models import Base, Notes, Labels, get_db_session
from .schemas import BaseResponseModel, NotesCreationSchema, NotesResponseSchema, NotesResponseModel, LabelsCreationSchema, LabelsResponseSchema, LabelsResponse
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import APIKeyHeader
from .utils import auth_user
import loggers

app = FastAPI(dependencies = [Security(APIKeyHeader(name = "Authorization")), Depends(auth_user)])

log_file = "fundoo_notes.log"
logger = loggers.setup_logger(log_file)

@app.post('/notecreate', response_model=NotesResponseSchema)
def add_note(note: NotesCreationSchema, request: Request, db: Session = Depends(get_db_session)):
    logger.info("Creating a new Note for the User: %s", request.state.user_id)
    new_note = Notes(
        title=note.title,
        description=note.description,
        color=note.color,
        is_archive = note.is_archive,
        is_trash = note.is_trash,
        user_id= request.state.user_id
    )
    if not new_note:
        logger.exception(msg = "There was an Exception that occured while creating the note for")
        raise HTTPException(detail="error")
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    logger.info("Note created successfully...")
    return {"message": "Note Created Successfully", "status": 200, "data": new_note}

@app.get('/notes/', response_model=NotesResponseModel)
def get_notes(request: Request, db: Session = Depends(get_db_session)):
    logger.info("Reading all Notes for the User: %s", request.state.user_id)
    notes = db.query(Notes).filter(Notes.user_id == request.state.user_id).all()
    if not notes:
        logger.exception(msg = "There was an Exception that occured while reading the note")
        raise HTTPException(status_code=404, detail="No notes found")
    logger.info("Note read successfully...")
    return {"message": "Notes Retrieved Successfully", "status": 200, "data": notes}

@app.put('/notes/{note_id}', response_model=NotesResponseSchema)
def update_note(request: Request, note_id: int, note_payload: NotesCreationSchema, db: Session = Depends(get_db_session)):
    logger.info("Updating the Note for the User: %s", request.state.user_id)
    note = db.query(Notes).filter(Notes.user_id == request.state.user_id, Notes.id == note_id).first()
    if not note:
        logger.exception(msg = "There was an Exception that occured while updating")
        raise HTTPException(status_code=404, detail="Note not found")
    
    note.title = note_payload.title
    note.description = note_payload.description
    db.commit()
    db.refresh(note)
    logger.info("Note updated successfully...")
    return {"message": "Note Updated Successfully", "status": 200, "data":  note}

@app.delete('/notes/{note_id}', response_model=BaseResponseModel)
def delete_note(request: Request, note_id: int, db: Session = Depends(get_db_session)):
    logger.info("deleting the Note for the User: {request.state.user_id}")
    note = db.query(Notes).filter(Notes.id == note_id, Notes.user_id == request.state.user_id).first()
    if not note:
        logger.exception(msg = "There was an Exception that occured while deleting the note")
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(note)
    db.commit()
    logger.info("Note deleted successfully...")
    return {"message": "Note deleted successully", "status": 200}


@app.patch("/notes/{note_id}/archive", response_model = NotesResponseSchema)
def archive_note(request: Request, note_id: int, archive: bool, db: Session = Depends(get_db_session)):
    logger.info("Archiving Note for the User: {request.state.user_id}")
    note = db.query(Notes).filter(Notes.id == note_id, Notes.user_id == request.state.user_id).first()
    if not note:
        logger.exception(msg = "There was an Exception that occured while archiving the note")
        raise HTTPException(detail = "Note Not Found", status_code = 404)
    note.is_archive = archive
    db.commit()
    db.refresh(note)
    status = "Archived" if archive else "Unarchived"
    logger.info("Note archived successfully...")
    return {"message": f"Note {status} Successfully", "status": 200, "data": note}

@app.patch("/notes/{note_id}/trash", response_model = NotesResponseSchema)
def trash_note(request: Request, note_id: int, trash: bool, db: Session = Depends(get_db_session)):
    logger.info("Making a Note to be trash for the User: {request.state.user_id}")
    note = db.query(Notes).filter(Notes.id == note_id, Notes.user_id == request.state.user_id).first()
    if not note:
        logger.exception(msg = "There was an Exception that occured while trashing the note")
        raise HTTPException(detail = "Note Not Found", status_code = 404)
    note.is_trash = trash
    db.commit()
    db.refresh(note)
    status = "Trashed" if trash else "Present"
    logger.info("Note Trashed successfully...")
    return {"message": f"Note {status} Successfully", "status": 200, "data": note}

@app.get('/notes/getArchive', response_model= NotesResponseModel)
def get_archive_notes(request: Request, db: Session = Depends(get_db_session)):
    logger.info("Reading a archive Note for the User")
    notes = db.query(Notes).filter(Notes.user_id == request.state.user_id, Notes.is_archive == True, Notes.is_trash == False).all()
    if not notes:
        logger.exception(msg = "There was an Exception that occured while reading the archive note")
        raise HTTPException(status_code=404, detail="No notes found")
    logger.info("Archive Note read successfully...")
    return {"message": "Notes Archived Successfully", "status": 200, "data": notes}

@app.get('/notes/getTrash', response_model=NotesResponseModel)
def get_trash_notes(request: Request, db: Session = Depends(get_db_session)):
    logger.info("Reading a trash Note for the User")
    notes = db.query(Notes).filter(Notes.user_id == request.state.user_id, Notes.is_trash == True).all()
    if not notes:
        logger.exception(msg = "There was an Exception that occured while reading the trash note")
        raise HTTPException(status_code=404, detail="No notes found")
    logger.info("Trash Note read successfully...")
    return {"message": "Notes Deleted Successfully", "status": 200, "data": notes}


@app.post('/labelcreate', response_model=LabelsResponseSchema)
def add_label(label: LabelsCreationSchema, request: Request, db: Session = Depends(get_db_session)):
    logger.info("Creating a new label for the User")
    new_label = Labels(
        label_name = label.label_name,
        user_id = request.state.user_id
    )
    if not new_label:
        logger.exception(msg = "There was an Exception that occured while creating the label")
        raise HTTPException(detail="error")
    db.add(new_label)
    db.commit()
    db.refresh(new_label)
    logger.info("Label created successfully...")
    return {"message": "Label Created Successfully", "status": 200, "data": label}

@app.get('/labels/', response_model=LabelsResponse)
def get_labels(request: Request, db: Session = Depends(get_db_session)):
    logger.info("Readin all label for the User")
    label = db.query(Labels).filter(Labels.user_id == request.state.user_id).all()
    if not label:
        logger.exception(msg = "There was an Exception that occured while reading the lable")
        raise HTTPException(status_code=404, detail="No notes found")
    logger.info("Label read successfully...")
    return {"message": "Labels Retrieved Successfully", "status": 200, "data": label}

@app.put('/labels/{label_id}', response_model=LabelsResponseSchema)
def update_note(request: Request, label_id: int, label_payload: LabelsCreationSchema, db: Session = Depends(get_db_session)):
    logger.info("Updating a label for the User")
    label = db.query(Labels).filter(Labels.user_id == request.state.user_id, Labels.id == label_id).first()
    if not label:
        logger.exception(msg = "There was an Exception that occured while updating the label")
        raise HTTPException(status_code=404, detail="Note not found")
    
    label.label_name = label_payload.label_name
    db.commit()
    db.refresh(label)
    logger.info("Label updated successfully...")
    return {"message": "Label Updated Successfully", "status": 200, "data":  label}

@app.delete('/labels/{label_id}', response_model=BaseResponseModel)
def delete_note(request: Request, label_id: int, db: Session = Depends(get_db_session)):
    logger.info("Deleting a  label for the User")
    label = db.query(Labels).filter(Labels.id == label_id, Labels.user_id == request.state.user_id).first()
    if not label:
        logger.exception(msg = "There was an Exception that occured while deleting the label")
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(label)
    db.commit()
    logger.info("Label deleted successfully...")
    return {"message": "Label deleted successully", "status": 200}