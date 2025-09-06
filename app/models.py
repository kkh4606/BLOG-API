from sqlalchemy import Column, Integer, String, text, ForeignKey, Boolean
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from .database import Base


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))

    post = relationship("Posts", back_populates="owner")


class Posts(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default="TRUE")
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    owner = relationship("Users", back_populates="post")
    comment = relationship("Comment", back_populates="post")


class Vote(Base):
    __tablename__ = "votes"
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True)


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"))

    post = relationship("Posts", back_populates="comment")
