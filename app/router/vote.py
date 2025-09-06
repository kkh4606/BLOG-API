from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from .. import schema, database, models, util, oauth2
from typing import Optional, List


router = APIRouter(tags=["VOTE"])


@router.post("/posts/vote", status_code=status.HTTP_201_CREATED)
async def vote_post(
    vote: schema.Vote,
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    print(type(vote.post_id))

    post = db.query(models.Posts).filter(models.Posts.id == vote.post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id : {vote.post_id} not found",
        )

    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id
    )

    found_vote = vote_query.first()

    if vote.dir == 1:
        if found_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"already voted with id : {current_user.id}",
            )
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "successfully voted"}
    else:
        if not found_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="vote not found"
            )

        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "successfully deleted vote"}
