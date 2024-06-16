from fastapi import Request, HTTPException, status
import requests
from setting import settings
import loggers
import redis
import json
from datetime import datetime

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


class RedisManager:
    client = redis.Redis()

    @staticmethod
    def convert_datetime(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    @classmethod
    def save(cls, payload):
        user_id = payload.get('user_id')
        note_id = payload.get('id')
        serialized_payload = json.dumps(payload, default=cls.convert_datetime)

        if not user_id:
            logger.error("User ID is missing in the payload")
            raise ValueError("User ID is missing in the payload")

        if not note_id:
            logger.error("Note ID is missing in the payload")
            raise ValueError("Note ID is missing in the payload")

        if not serialized_payload:
            logger.error("Serialized payload is empty")
            raise ValueError("Serialized payload is empty")

        cls.client.hset(name=user_id, key=note_id, value=serialized_payload)

    @classmethod
    def retrieve(cls, user_id, note_id=None):
        try:
            if note_id:
                data = cls.client.hget(name=user_id, key=note_id)
                if data:
                    return json.loads(data)
                else:
                    return None
            else:
                data = cls.client.hgetall(name=user_id)
                if data:
                    return {key.decode(): json.loads(value) for key, value in data.items()}
                else:
                    return None
        except redis.RedisError as e:
            logger.error(f"Redis error occurred: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return None

    @classmethod
    def delete(cls, user_id, note_id):
        try:
            result = cls.client.hdel(user_id, note_id)
            if result:
                print(f"Note with id {note_id} deleted successfully for user_id {user_id}")
                return True
            else:
                print(f"Note with id {note_id} not found for user_id {user_id}")
                return False
        except redis.RedisError as e:
            logger.error(f"Redis error occurred: {e}")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return False
