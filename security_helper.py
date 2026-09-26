from datetime import datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_STRING = "MUHAMMAD_QURAN_HAQ"
ALGORITHM = "HS256"
SESSION_TIMEOUT = 30


def generate_access_token(user: dict, expire_duration: int = 30):

    # creating a shallow copy.
    to_encode = user.copy()
    token_expires_on = datetime.now() + timedelta(minutes=expire_duration)
    to_encode.update({"expiry": token_expires_on})

    return jwt.encode(to_encode, algorithm=ALGORITHM, key=SECRET_STRING)


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
