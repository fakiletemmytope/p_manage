from fastapi.security import OAuth2PasswordBearer
from passlib.hash import bcrypt
from datetime import datetime, timedelta
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError



def password_verification(password, hash):
    check = bcrypt.verify(password, hash)
    return check

SECRET_KEY = "e434573e0c4a5f0ebb67d41df3a2b400ae315b38ef74279614e33403dd17a04a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 25

current_user = None

def get_token(payload):
    expiration_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload["exp"] =  expiration_time
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def authenticate_token(token):
    global current_user
    try:    
        decoded = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)    
        # current_user = {
        #     "current_user_name": decoded["username"],
        #     "current_userId": decoded["id"]
        # }
        # print(current_user)
        return decoded
    except ExpiredSignatureError:
        print("Token has expired.")
        return None
    except InvalidTokenError:
        print("Invalid token.")
        return None

def hash_password(password):
    return bcrypt.using(rounds=13).hash(password)
