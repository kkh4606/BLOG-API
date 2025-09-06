from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from .. import schema, database, models, util, oauth2
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(tags=["AUTHENTICATION"])


@router.post("/login", response_model=schema.Token)
async def user_login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
):
    user = (
        db.query(models.Users)
        .filter(models.Users.email == user_credentials.username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not util.verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # create token if credential is valid

    access_token = oauth2.create_access_token(data={"user_id": int(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}
