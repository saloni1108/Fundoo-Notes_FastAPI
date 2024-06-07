from pydantic import BaseModel, Field, field_validator
import re

class BaseResponseModel(BaseModel):
    message: str
    status: int

class UserRegistrationSchema(BaseModel):
    user_name: str = Field(min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$", description="Username must be between 3 and 50 characters long and can contain letters, numbers, hyphens, and underscores.")
    password: str = Field(min_length=8, max_length=250, description="Password must be between 8 and 250 characters long.")
    first_name: str = Field(min_length=1, max_length=20, description="First name must be between 1 and 20 characters long.")
    last_name: str = Field(min_length=1, max_length=20, description="Last name must be between 1 and 20 characters long.")

    @field_validator('password')
    def validate_password(cls, v):
        if (len(v) < 8 or
            not re.search("[a-z]", v) or
            not re.search("[A-Z]", v) or
            not re.search("[0-9]", v) or
            not re.search("[@$!%*?&]", v)):
            raise ValueError("Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character.")
        return v
    

class UserLoginSchema(BaseModel):
    user_name: str = Field(min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$", description="Username must be between 3 and 50 characters long and can contain letters, numbers, hyphens, and underscores.")
    password: str = Field(min_length=8, max_length=250, description="Password must be between 8 and 250 characters long.")

class UserResponseSchema(BaseResponseModel):
    data: UserRegistrationSchema

