from sqlalchemy import Boolean, Column, BIGINT, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship

from api.db import Base

class Member(Base):
  __tablename__ = 'member'

  id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
  provider_id = Column(BIGINT, nullable=False)
  provider_type = Column(String(30), nullable=False)
  nickname = Column(String(12), nullable=False)
  status = Column(String(12), default="ACTIVATE", nullable=False)

  resume = relationship("Resume", back_populates="member")

class Resume(Base):
  __tablename__ = 'resume'

  id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
  member_id = Column(BIGINT, ForeignKey("member.id"), nullable=False)
  contents = Column(String(5000), nullable=False)
  public = Column(Boolean, default="True", nullable=False)

  member = relationship("Member", back_populates="resume")

class Post(Base):
  __tablename__ = 'post'

  id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
  author_id = Column(BIGINT, ForeignKey("member.id"), nullable=False)
  category_id = Column(BIGINT, ForeignKey("category.id"), nullable=False)
  title = Column(String(50), nullable=False)
  contents = Column(String(5000), nullable=False)
  create_at = Column(TIMESTAMP)
  update_at = Column(TIMESTAMP)
  deadline = Column(TIMESTAMP)
  max_member = Column(BIGINT)


  category = relationship("Category", back_populates="post")


class Category(Base):
  __tablename__ = 'category'

  id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
  name =  Column(String(30), nullable=False)

  post = relationship("Post", back_populates="category")
