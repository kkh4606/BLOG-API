from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from .. import schema, database, models, util, oauth2


router = APIRouter(tags=["USERS"])


@router.get("/users")
async def get_users():
    pass


@router.get("/users/{id}")
async def get_user():
    pass


@router.post(
    "/users/create", response_model=schema.UserOut, status_code=status.HTTP_201_CREATED
)
async def create_user(user: schema.UserCreate, db: Session = Depends(database.get_db)):

    hashed_password = util.hash_password(user.password)
    user.password = hashed_password
    new_user = models.Users(**user.model_dump())

    db.add(new_user)
    db.commit()
    access_token = oauth2.create_access_token(data={"user_id": int(new_user.id)})

    db.refresh(new_user)

    return {
        "id": new_user.id,
        "email": new_user.email,
        "created_at": new_user.created_at,
        "token": {"access_token": access_token, "token_type": "bearer"},
    }


@router.put("/users/{id}")
async def update_user():
    pass
