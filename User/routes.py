from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session, Query
from sqlalchemy.exc import SQLAlchemyError
from .models import User, get_db_session
from .schemas import UserRegistrationSchema, UserLoginSchema, UserResponseSchema, BaseResponseModel
from .utils import get_password_hash, verify_password, encoded_user_jwt, decoded_user_jwt, Audience, send_email
from setting import settings
from smtplib import SMTPAuthenticationError

app = FastAPI()

@app.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponseSchema, response_model_exclude = {"data": ["password"]})
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
        email = user.email,
        is_verified=False
    )
    
    try:
        db.add(new_user)
        db.commit()
        access_token = encoded_user_jwt({"user_id": new_user.id, "aud": Audience.register.value})
        db.refresh(new_user)
        send_email(to_mail = new_user.email, mail_subject = "Welcome to the application", 
                   mail_body = f"Hello {new_user.first_name},\n\nThank you for registering at our service. Please click the link given below to verify:\n\n 127.0.0.1:8000/verify_user?token={access_token}\n\nBest regards,\nFastAPI Team")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while creating the user")
    except SMTPAuthenticationError as e:
        raise HTTPException(status_code=500, detail= str(e))
    
    return {"message": "User registered successfully", "status": 201, "data": new_user}

@app.post('/login')
def login(user: UserLoginSchema, db: Session = Depends(get_db_session)):
    db_user = db.query(User).filter(User.user_name == user.user_name).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    if not db_user.is_verified:
        raise HTTPException(status_code = 400, detail = "User not found")
    access_token = encoded_user_jwt({"user_id": db_user.id, "aud": Audience.login.value})
    return {"message": "User Logged In Successfully", "status": 200, "token": access_token}

@app.get("/verify_user", response_model=BaseResponseModel)
def verify_user(token: str, db: Session = Depends(get_db_session)):
    try:
        payload = decoded_user_jwt(token=token, audience=Audience.register.value)
        user_id = payload.get("user_id")
        
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_verified = True
            db.commit()
        return {"message": "User verified successfully", "status": 200}
    
    except:
        raise HTTPException(status_code = 401, detail = "User not found and verified") 
    