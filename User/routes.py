from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .models import User, get_db_session
from .schemas import UserRegistrationSchema, UserLoginSchema, UserResponseSchema, BaseResponseModel
from .password_utils import get_password_hash, verify_password

app = FastAPI()

@app.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponseSchema)
def register_user(user: UserRegistrationSchema, db: Session = Depends(get_db_session)):
    user_exists = db.query(User).filter(User.user_name == user.user_name).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(
        user_name=user.user_name,
        password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        is_verified=False
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while creating the user")
    
    return {"message": "User registered successfully", "status": 201, "data": new_user}

@app.post('/login', response_model=BaseResponseModel)
def login(user: UserLoginSchema, db: Session = Depends(get_db_session)):
    db_user = db.query(User).filter(User.user_name == user.user_name).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    return {"message": "User Logged In Successfully", "status": 200}
