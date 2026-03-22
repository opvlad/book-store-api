import bcrypt


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    password_bytes = password.encode("utf-8")
    password_hash_bytes = bcrypt.hashpw(password_bytes, salt)
    return password_hash_bytes.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    plain_password_bytes = plain_password.encode("utf-8")
    password_hash_bytes = password_hash.encode("utf-8")
    return bcrypt.checkpw(plain_password_bytes, password_hash_bytes)
