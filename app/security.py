from datetime import timedelta, datetime, UTC
import bcrypt
import jwt


from app.config import settings


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    password_bytes = password.encode("utf-8")
    password_hash_bytes = bcrypt.hashpw(password_bytes, salt)
    return password_hash_bytes.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    plain_password_bytes = plain_password.encode("utf-8")
    password_hash_bytes = password_hash.encode("utf-8")
    return bcrypt.checkpw(plain_password_bytes, password_hash_bytes)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, settings.algorithm)


def decode_token(token: str) -> dict | None:
    try:
        decoded = jwt.decode(token, settings.secret_key, settings.algorithm)
        return decoded
    except jwt.InvalidTokenError:
        return None
