from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session, joinedload
from .. import schema, database, models, util, oauth2
from typing import Optional, List
from sqlalchemy import func


router = APIRouter(tags=["POSTS"])


# @router.get("/posts")
@router.get("/posts", response_model=List[schema.PostOut])
async def get_posts(
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(database.get_db),
    search: Optional[str] = "",
    skip: int = 0,
    limit: int = 0,
):

    posts = (
        db.query(
            models.Posts,
            func.count(models.Vote.post_id).label("vote"),
            func.count(models.Comment.id).label("comment"),
        )
        .outerjoin(models.Vote, models.Vote.post_id == models.Posts.id)
        .outerjoin(models.Comment, models.Comment.post_id == models.Posts.id)
        .options(joinedload(models.Posts.owner))
        .options(joinedload(models.Posts.comment))
        .group_by(models.Posts.id)
        .all()
    )

    return [
        {"Post": post, "vote": vote, "comment": comment}
        for post, vote, comment in posts
    ]


@router.get("/posts/{id}")
async def get_post(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    post = db.query(models.Posts).filter(models.Posts.id == id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id : {id} not found",
        )
    return post


@router.post("/posts/create")
async def create_post(
    post: schema.CreatePost,
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    new_post = models.Posts(**post.model_dump(), owner_id=current_user.id)

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.put("/posts/{id}", response_model=schema.Post)
async def update_post(
    id: int,
    post_update: schema.PostBase,
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    post_query = db.query(models.Posts).filter(models.Posts.id == id)
    post = post_query.first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id : {id} not found",
        )

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="invalid credentials to perform request action",
        )

    post_query.update(post_update.model_dump(), synchronize_session=False)
    db.commit()

    return post


@router.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    post_query = db.query(models.Posts).filter(models.Posts.id == id)
    post = post_query.first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id : {id} not found",
        )

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="invalid credentials to perform request action",
        )

    post_query.delete(synchronize_session=False)
    db.commit()
    return
