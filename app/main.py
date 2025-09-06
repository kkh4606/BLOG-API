from fastapi import FastAPI
from . import models
from app.router import user, auth, post, vote, comment


from .database import engine

# models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(post.router)
app.include_router(vote.router)
app.include_router(comment.router)


@app.get("/")
def greeting():
    return {"message": "hello world"}
