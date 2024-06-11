from fastapi import Request, HTTPException
from User.utils import decoded_user_jwt, Audience
import requests

def auth_user(request: Request):
    token = request.headers.get('authorization')
    if not token:
        raise HTTPException(status_code=401, detail="Authorization token is missing")
    response = requests.get(url = "http://127.0.0.1:8000/fetchUser", params = {"token": token})
    if response.status_code != 200:
        raise HTTPException(detail = "User Authentication failed", status_code = response.status_code)
    
    user_id = response.json().get("id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="User ID not found in token")
    request.state.user_id = user_id