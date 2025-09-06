from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from . import schema, models, database
from .config import settings
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status


oauth2_scheme = OAuth2PasswordBearer("login")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str, credential_exceptions):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")  # type:ignore

        if id is None:
            raise credential_exceptions

        tokenData = schema.TokenData(id=str(id))

    except JWTError:
        raise credential_exceptions
    return tokenData


def get_current_user(
    token: Session = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db),
):

    credential_exceptions = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="could not validate credentials",
    )

    token = verify_access_token(token, credential_exceptions)  # type:ignore
    user = db.query(models.Users).filter(models.Users.id == int(token.id)).first()
    return user
