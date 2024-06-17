from pydantic import BaseModel, Field, field_validator
import re
import loggers

log_file = "fundoo_notes.log"
logger = loggers.setup_logger(log_file)

class BaseResponseModel(BaseModel):
    message: str
    status: int

class UserRegistrationSchema(BaseModel):
    user_name: str = Field(min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$", description="Username must be between 3 and 50 characters long and can contain letters, numbers, hyphens, and underscores.")
    password: str = Field(min_length=8, max_length=250, description="Password must be between 8 and 250 characters long.")
    first_name: str = Field(min_length=1, max_length=20, description="First name must be between 1 and 20 characters long.")
    last_name: str = Field(min_length=1, max_length=20, description="Last name must be between 1 and 20 characters long.")
    email: str = Field(description = "THe Email entered should be valid")

    @field_validator('password')
    def validate_password(cls, v):
        if (len(v) < 8 or
            not re.search("[a-z]", v) or
            not re.search("[A-Z]", v) or
            not re.search("[0-9]", v) or
            not re.search("[@$!%*?&]", v)):
            logger.exception("Password incorrect")
            raise ValueError("Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character.")
        return v
    
    @field_validator('email')
    def validate_email(cls, v):
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, v):
            logger.exception("Invalid Email")
            raise ValueError("Invalid email address")
        return v

class UserSchema(UserRegistrationSchema):
    id: int   

class UserLoginSchema(BaseModel):
    user_name: str = Field(min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$", description="Username must be between 3 and 50 characters long and can contain letters, numbers, hyphens, and underscores.")
    password: str = Field(min_length=8, max_length=250, description="Password must be between 8 and 250 characters long.")

class UserResponseSchema(BaseResponseModel):
    data: UserSchema

class ForgotPasswordSchema(BaseModel):
    email: str = Field(description="The email associated with the user account")

    @field_validator('email')
    def validate_email(cls, v):
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, v):
            logger.exception("Invalid Email")
            raise ValueError("Invalid email address")
        return v

class ResetPasswordSchema(BaseModel):
    password: str = Field(min_length=8, max_length=250, description="Password must be between 8 and 250 characters long.")

    @field_validator('password')
    def validate_password(cls, v):
        if (len(v) < 8 or
            not re.search("[a-z]", v) or
            not re.search("[A-Z]", v) or
            not re.search("[0-9]", v) or
            not re.search("[@$!%*?&]", v)):
            logger.exception("Password incorrect")
            raise ValueError("Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character.")
        return v