from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional, List
from pydantic.types import conint


class User(BaseModel):
    email: EmailStr
    password: str
    phone_number: str


class UserCreate(User):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class UserOut(BaseModel):
    id: int
    email: str
    phone_number: str
    created_at: datetime
    token: Token


class UserPostOut(BaseModel):
    id: int
    email: str
    phone_number: str
    created_at: datetime


class TokenData(BaseModel):
    id: str


class PostBase(BaseModel):
    title: Optional[str]
    content: str
    published: bool


class CreatePost(PostBase):
    pass


class Comment(BaseModel):
    post_id: int
    content: str


class CommentUpdate(BaseModel):
    content: str


class CommentOut(BaseModel):
    id: int
    post_id: int
    user_id: int
    content: str
    created_at: datetime


class CommentDelete(BaseModel):
    post_id: int


class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserPostOut
    comment: List[CommentOut] = []


class PostOut(BaseModel):
    Post: Post
    like: int
    comment: int

    class Config:
        from_attributes = True


class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)
