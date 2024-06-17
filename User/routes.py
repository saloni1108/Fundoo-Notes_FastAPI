from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session, Query
from sqlalchemy.exc import SQLAlchemyError
from .models import User, get_db_session
from .schemas import UserRegistrationSchema, UserLoginSchema, UserResponseSchema, BaseResponseModel, UserSchema, ForgotPasswordSchema, ResetPasswordSchema
from .utils import get_password_hash, verify_password, encoded_user_jwt, decoded_user_jwt, Audience, send_email
from setting import settings
from smtplib import SMTPAuthenticationError
import loggers
from Core import create_app

app = create_app(name = "user")

log_file = "fundoo_notes.log"
logger = loggers.setup_logger(log_file)

@app.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponseSchema, response_model_exclude = {"data": ["password"]})
def register_user(user: UserRegistrationSchema, db: Session = Depends(get_db_session)):
    logger.info("Registering the user...")
    user_exists = db.query(User).filter(User.user_name == user.user_name).first()
    if user_exists:
        logger.exception("User already Exists")
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
        logger.exception("User cannot be created")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while creating the user")
    except SMTPAuthenticationError as e:
        logger.exception(str(e))
        raise HTTPException(status_code=500, detail= str(e))
    logger.info("User registered successfully")
    return {"message": "User registered successfully", "status": 201, "data": new_user}

@app.post('/login')
def login(user: UserLoginSchema, db: Session = Depends(get_db_session)):
    logger.info("Logging in the user")
    db_user = db.query(User).filter(User.user_name == user.user_name).first()
    if not db_user or not verify_password(user.password, db_user.password):
        logger.exception("Invalid Username or Password")
        raise HTTPException(status_code=400, detail="Invalid username or password")
    if not db_user.is_verified:
        logger.exception("User not found")
        raise HTTPException(status_code = 400, detail = "User not found")
    access_token = encoded_user_jwt({"user_id": db_user.id, "aud": Audience.login.value})
    logger.info("User logged in Successfully")
    return {"message": "User Logged In Successfully", "status": 200, "token": access_token}

@app.get("/verify_user", response_model=BaseResponseModel)
def verify_user(token: str, db: Session = Depends(get_db_session)):
    logger.info("Verifying the user")
    try:
        payload = decoded_user_jwt(token=token, audience=Audience.register.value)
        user_id = payload.get("user_id")
        
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_verified = True
            db.commit()
        logger.info("User Verified")
        return {"message": "User verified successfully", "status": 200}
    
    except:
        logger.exception("User not verified")
        raise HTTPException(status_code = 401, detail = "User not found and verified") 
    

@app.get("/fetchUser", response_model=UserSchema, status_code=status.HTTP_200_OK, include_in_schema=False)
def fetch_user(token: str, db: Session = Depends(get_db_session)):
    logger.info("Fetching a user...")
    try:
        payload = decoded_user_jwt(token=token, audience=Audience.login.value)
        user_id = payload.get("user_id")
        if user_id is None:
            logger.exception("Invalid token entered")
            raise HTTPException(status_code=400, detail="Invalid token: user ID not found")
        user = db.query(User).where(User.id == user_id).first()
        if user is None:
            logger.exception("user not found")
            raise HTTPException(status_code=404, detail="User not found")
        logger.info("User fetched...")
        return user
    except SQLAlchemyError as e:
        logger.exception(str(e))
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except Exception as e:
        logger.exception(str(e))
        raise HTTPException(status_code=400, detail="Invalid token: " + str(e)) 
    
@app.post('/forgot-password', response_model=BaseResponseModel)
def forgot_password(user: ForgotPasswordSchema, db: Session = Depends(get_db_session)):
    logger.info("Processing Forgot password Request...")
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        logger.exception("Email not Found")
        raise HTTPException(status_code=404, detail="Email not found")

    reset_token = encoded_user_jwt({"user_id": db_user.id, "aud": Audience.reset_password.value})
    try:
        send_email(to_mail = db_user.email, mail_subject = "Password Reset Request", mail_body = f"Hello {db_user.first_name},\n\nPlease use the following link to reset your password:\n\n127.0.0.1:8000/reset-password?token={reset_token}\n\nBest regards,\nFastAPI Team")
        logger.info("Password reset email sent")
        return {"message": "Password reset mail sent successfully", "status": 200}
    except SMTPAuthenticationError as e:
        logger.exception(str(e))
        raise HTTPException(status_code=500, detail=str(e))


    
@app.post('/reset-password', response_model=BaseResponseModel)
def reset_password(token: str, new_password: ResetPasswordSchema, db: Session = Depends(get_db_session)):
    logger.info("Resetting the user's password")
    try:
        payload = decoded_user_jwt(token=token, audience=Audience.reset_password.value)
        user_id = payload.get("user_id")
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            logger.exception("User not found")
            raise HTTPException(status_code=404, detail="User not found")
        
        hashed_password = get_password_hash(new_password.password)
        user.password = hashed_password
        db.commit()
        
        logger.info("Password reset successfully")
        return {"message": "Password reset successfully", "status": 200}
    except SQLAlchemyError as e:
        logger.exception(str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except Exception as e:
        logger.exception(str(e))
        raise HTTPException(status_code=400, detail="Invalid token: " + str(e))