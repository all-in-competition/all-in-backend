from sqlalchemy import *
from sqlalchemy.dialects.mysql import TINYINT, INTEGER, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

Base = declarative_base()


#회원 정보
class Member(Base):
  __tablename__ = 'member'

  id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
  provider_id = Column(String(255), nullable=False)
  provider_type = Column(String(30), nullable=False)
  nickname = Column(String(12), nullable=False)
  status = Column(String(12), default="ACTIVE")

  tag = relationship("Tag", secondary=member_tag, back_populates="member")
  resume = relationship("Resume", back_populates="member")
  alarm = relationship("Alarm", back_populates="member")
  post = relationship("Board", back_populates="member")
  like = relationship("Like", back_populates="member")
  comment = relationship("Comment", back_populates="member")
  chatroom = relationship("MemberChatroom", back_populates="member")
  message = relationship("Message", back_populates="member")

#이력서
class Resume(Base):
  __tablename__ = 'resume'

  id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
  member_id = Column(BIGINT, ForeignKey('member.id'), nullable=False)
  contents = Column(String(5000), nullable=False)
  public = Column(Boolean, nullable=False)

  member = relationship("Member", back_populates="resume")
  tag = relationship("Tag", secondary=resume_tag, back_populates="resume")

#게시판
class Board(Base):
  __tablename__ = 'post'

  id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
  author_id = Column(BIGINT, ForeignKey('member.id'), nullable=False)
  category_id = Column(BIGINT, ForeignKey('category.id'), nullable=False)
  title = Column(String(50), nullable=False)
  contents = Column(String(5000), nullable=False)
  create_at = Column(TIMESTAMP, default=func.current_timestamp, nullable=False)
  update_at = Column(TIMESTAMP, default=func.current_timestamp, nullable=False)
  deadline = Column(TIMESTAMP, func.current_time, nullable=False)
  max_member = Column(TINYINT(unsigned=True), nullable=False, default=0)
  view_count = Column(INTEGER(unsigned=True), nullable=False, default=0)
  like_count = Column(INTEGER(unsigned=True), nullable=False, default=0)
  current_member = Column(TINYINT(unsigned=True), nullable=False, default=0)
  status = Column(String(12), nullable=False, default="ACTIVE")

  member = relationship("Member", back_populates="post")
  alarm = relationship("Alarm", back_populates="post")
  tag = relationship("Tag", secondary=post_tag, back_populates="post")
  like = relationship("Like", back_populates="post")
  comment = relationship("Comment", back_populates="post")
  chatroom = relationship("Chatroom", back_populates="post")

#좋아요
class Like(Base):
  __tablename__ = 'like'

  id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
  post_id = Column(BIGINT, ForeignKey('post.id'), nullable=False)
  user_id = Column(BIGINT, ForeignKey('member.id'), nullable=False)

  member = relationship("Member", back_populates="like")
  post = relationship("Post", back_populates="like")

#댓글
class Comment(Base):
  __tablename__ = 'comment'

  id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
  post_id = Column(BIGINT, ForeignKey('post.id'), nullable=False)
  user_id = Column(BIGINT, ForeignKey('member.id'), nullable=False)
  parent_id = Column(BIGINT, ForeignKey('comment.id'))
  content = Column(String(255), nullable=False)
  status = Column(String(20), nullable=False)
  create_at = Column(TIMESTAMP, nullable=False, default=func.current_timestamp)
  update_at = Column(TIMESTAMP, nullable=False, default=func.current_timestamp)

  member = relationship("Member", back_populates="comment")
  post = relationship("Post", back_populates="comment")

#카테고리
class Category(Base):
  __tablename__ = 'category'

  id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
  name = Column(String(30), nullable=False)

  post = relationship("Board", back_populates="category")

#알람
class Alarm(Base):
    __tablename__ = 'alarm'

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    sender_id = Column(BIGINT, ForeignKey('member.id'), nullable=False)
    receiver_id = Column(BIGINT, ForeignKey('member.id'), nullable=False)
    post_id = Column(BIGINT, ForeignKey('post.id'), nullable=False)
    type = Column(TINYINT(unsigned=True), nullable=False)
    contents = Column(String(255))

    member = relationship("Member", back_populates="alarm")
    post = relationship("Post", back_populates="alarm")

#채팅방
class Chatroom(Base):
  __tablename__ = 'chatroom'

  id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
  post_id = Column(BIGINT, ForeignKey('post.id'), nullable=False)

  post = relationship("Post", back_populates="chatroom")
  message = relationship("Message", back_populates="chatroom")

#채팅방 참가 멤버
class MemberChatroom(Base):
  __tablename__ = 'member_chatroom'
  
  id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
  chatroom_id = Column(BIGINT, ForeignKey('chatroom.id'), nullable=False)
  member_id = Column(BIGINT, ForeignKey('member.id'), nullable=False)

  member = relationship("Member", back_populates="chatroom")
  chatroom = relationship("Chatroom", back_populates="member")

#채팅내역
class Message(Base):
  __tablename__ = 'message'

  id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
  chatroom_id = Column(BIGINT, ForeignKey('chatroom.id'), nullable=False)
  member_id = Column(BIGINT, ForeignKey('member.id'), nullable=False)
  contents = Column(String(255), nullable=False)
  create_at = Column(TIMESTAMP, default=func.current_timestamp, nullable=False)

  member = relationship("Member", back_populates="message")
  chatroom = relationship("Chatroom", back_populates="message")

member_tag = Table(
  "MemberTag",
  Base.metadata,
  Column("tag_id", ForegnKey("tag.id"), primary_key=True),
  Column("member_id", ForeignKey("member.id"), primary_key=True)
)

post_tag = Table(
  "PostTag",
  Base.metadata,
  Column("tag_id", ForegnKey("tag.id"), primary_key=True),
  Column("post_id", ForeignKey("post.id"), primary_key=True)
)

resume_tag = Table(
  "ResumeTag",
  Base.metadata,
  Column("tag_id", ForegnKey("tag.id"), primary_key=True),
  Column("resume_id", ForeignKey("resume.id"), primary_key=True)
)

#태그
class Tag():
  __tablename__ = 'tag'

  id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
  name = Column(String(30), nullable=False)
  use_count = Column(Integer, nullable=False, default=0)

  member = relationship("Member", secondary=member_tag, back_populates="tag")
  post = relationship("Board", secondary=post_tag, back_populates="tag")
  resume = relationship("Resume", secondary=resume_tag, back_populates="tag")


# #관심태그 sqlalchemy model
# class MemberTag(Base):
#   __tablename__ = 'member_tag'
#
#   id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
#   tag_id = Column(BIGINT, ForeignKey('tag.id'), nullable=False)
#   member_id = Column(BIGINT, ForeignKey('member.id'), nullable=False)
#
#   member = relationship("Member", back_populates="tag")
#   tag = relationship("Tag", back_populates="member")
#
# #게시글 태그
# class BoardTag(Base):
#   __tablename__ = 'post_tag'
#
#   id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
#   post_id = Column(BIGINT, ForeignKey('post.id'), nullable=False)
#   tag_id = Column(BIGINT, ForeignKey('tag.id'), nullable=False)
#
#   post = relationship("Post", back_populates="tag")
#   tag = relationship("Tag", back_populates="post")
#
# #이력서 태그
# class ResumeTag(Base):
#   __tablename__ = 'resume_tag'
#
#   id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
#   resume_id = Column(BIGINT, ForeignKey('resume.id'), nullable=False)
#   tag_id = Column(BIGINT, ForeignKey('tag.id'), nullable=False)
#
#   resume = relationship("Resume", back_populates="tag")
#   tag = relationship("Tag", back_populates="resume")