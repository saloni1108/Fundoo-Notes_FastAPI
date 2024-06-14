from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException, RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from smtplib import SMTPAuthenticationError
import loggers

log_file = "fundoo_notes.log"
logger = loggers.setup_logger(log_file)

def base_exception_handler(request: Request, exception: Exception):
    logger.error(f"Unexpected Error: {str(exception)} - Path: {request.url.path}")
    return JSONResponse(
        status_code = 500, 
        content = {"message": str(exception), "status": status.HTTP_500_INTERNAL_SERVER_ERROR})

def validation_exception_handler(request: Request, exception: RequestValidationError):
    logger.error(f"Validation Error: {exception.errors()} - Path: {request.url.path}")
    return JSONResponse(
        status_code=422,
        content={"message": "Validation error", "status": status.HTTP_422_UNPROCESSABLE_ENTITY, "details": exception.errors()},
    )

def http_exception_handler(request: Request, exception: HTTPException):
    logger.error(f"HTTP Exception: {exception.detail} - Path: {request.url.path}")
    return JSONResponse(
        status_code=exception.status_code,
        content={"message": exception.detail, "status": exception.status_code},
    )

def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database Error: {str(exc)} - Path: {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"message": "Database error", "status": status.HTTP_500_INTERNAL_SERVER_ERROR, "details": str(exc)},
    )

def smtp_authentication_error_handler(request: Request, exc: SMTPAuthenticationError):
    logger.error(f"SMTP Authentication Error: {str(exc)} - Path: {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"message": "SMTP authentication error", "status": status.HTTP_500_INTERNAL_SERVER_ERROR, "details": str(exc)},
    )

def create_app(name, dependencies = None):
    if not dependencies:
        app =  FastAPI(title = name)
    else:
        app =  FastAPI(title = name, dependencies = dependencies)
    app.add_exception_handler(Exception, base_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(SMTPAuthenticationError, smtp_authentication_error_handler)
    return app