from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
import jwt
from .db_config import settings
import uuid

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
GUEST_TOKEN_EXPIRE_MINUTES = settings.guest_token_expire_minutes

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire.timestamp()})
    print(f'Logged expiration: {expire}')

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def create_guest_token():
    guest_uuid = str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + timedelta(minutes=GUEST_TOKEN_EXPIRE_MINUTES)
    dictionary = dict(zip(['guest_user_id', 'exp'], [guest_uuid, expire]))

    encoded_jwt = jwt.encode(dictionary, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def decode_authorization_token_with_exception(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try: 
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de autentificare expirat")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de autentificare invalid")
    
def decode_authorization_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional)):
    if not credentials:
        return None
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de autentificare expirat")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de autentificare invalid")
    
def decode_guest_token_with_exception(guest_token: str = Cookie(None, alias="guestSessionToken")):
    try:
        payload = jwt.decode(guest_token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de autentificare expirat")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token de guest invalid")
    
def decode_guest_token(guest_token: str | None = Cookie(None, alias="guestSessionToken")):
    if not guest_token:
        return None
    try:
        payload = jwt.decode(guest_token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de autentificare expirat")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de autentificare invalid")

def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role = payload.get("role")
        if role != "admin":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Rolul de admin este necesar pentru a efectua aceasta actiune")
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalid")