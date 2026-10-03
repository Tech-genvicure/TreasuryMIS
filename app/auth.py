from fastapi import Request
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)

def current_user(request: Request):
    return request.session.get("user")

def require_login(request: Request):
    user = current_user(request)
    if not user:
        return None
    return user
