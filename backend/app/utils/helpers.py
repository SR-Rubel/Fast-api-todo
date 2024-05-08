import bcrypt


def get_hashed_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed_password: str) -> str:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())
