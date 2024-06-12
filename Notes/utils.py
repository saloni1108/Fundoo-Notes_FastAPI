from fastapi import Request, HTTPException
import requests
from setting import settings
import loggers

log_file = "fundoo_notes.log"
logger = loggers.setup_logger(log_file)

def auth_user(request: Request):
    logger.info("Authenticating the User...")
    token = request.headers.get('authorization')
    if not token:
        logger.exception("There was a error while authorization: the authorization token caused an error")
        raise HTTPException(status_code=401, detail="Authorization token is missing")
    response = requests.get(url = f"{settings.USER_URI}/fetchUser", params = {"token": token})
    if response.status_code != 200:
        logger.exception("There was a error while authorization")
        raise HTTPException(detail = "User Authentication failed", status_code = response.status_code)
    
    user_id = response.json().get("id")
    if user_id is None:
        logger.exception("There was a error while authorization: The userId not found")
        raise HTTPException(status_code=401, detail="User ID not found in token")
    logger.info("User authenticated successfully")
    request.state.user_id = user_id
    