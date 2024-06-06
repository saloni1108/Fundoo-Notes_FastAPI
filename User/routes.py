from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .models import User, get_db_session
from .schemas import UserRegistrationSchema, UserLoginSchema, UserResponseSchema
from .password_utils import get_password_hash, verify_password

app = FastAPI()

@app.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserRegistrationSchema, db: Session = Depends(get_db_session)):
    user_exists = db.query(User).filter(User.user_name == user.user_name).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(user.password)
    print(hashed_password)

    new_user = User(
        user_name=user.user_name,
        password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        is_verified=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}

@app.post('/login', response_model=UserResponseSchema)
def login(user: UserLoginSchema, db: Session = Depends(get_db_session)):
    db_user = db.query(User).filter(User.user_name == user.user_name).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    return {"Message": "User Logged In Successfully", "Status Code": 200}

