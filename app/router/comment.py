from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from .. import schema, database, models, util, oauth2
from typing import Optional, List
from sqlalchemy import func


router = APIRouter(tags=["COMMENTS"])


@router.post("/posts/comment")
async def comment_post(
    comment: schema.Comment,
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    post = db.query(models.Posts).filter(models.Posts.id == comment.post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="post not found"
        )

    new_comment = models.Comment(**comment.model_dump(), user_id=current_user.id)

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return {"message": "comment success"}


@router.put("/posts/comments/{id}")
def update_comment(
    id: int,
    post_id: int,
    comment_update: schema.CommentUpdate,
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    post = db.query(models.Posts).filter(models.Posts.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id : {post_id} not found",
        )

    comment_query = db.query(models.Comment).filter(models.Comment.id == id)
    comment = comment_query.first()

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"comment with id : {id} not found",
        )

    if current_user.id != comment.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="request action not allowed"
        )

    comment_query.update(comment_update.model_dump(), synchronize_session=False)
    db.commit()

    return {"message": "update comment success"}


@router.delete("/posts/comments/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    id: int,
    post_id: int,
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    post = db.query(models.Posts).filter(models.Posts.id == post_id).first()

    comment_query = db.query(models.Comment).filter(models.Comment.id == id)

    comment = comment_query.first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="post not found"
        )

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="comment not found"
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="request action not allowed"
        )

    comment_query.delete(synchronize_session=False)
    db.commit()
