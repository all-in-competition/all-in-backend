from typing import Sequence, Union
from api.models.model import Post, Tag, Like, post_tag, Chatroom
from api.schemas.like import LikeResponse
from api.schemas.member import MemberCreate
from fastapi import HTTPException
from fastapi_pagination.cursor import CursorParams
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from api.schemas.post import PostCreate, PostSummaryResponse, PostDetailResponse, PostResponse, PostUpdate
from starlette import status
from fastapi_pagination.ext.sqlalchemy import paginate


def post_to_summary_response(posts: Sequence[Post]) -> Union[Sequence[PostSummaryResponse], None]:
    return [PostSummaryResponse(
        author_name=post.member.nickname,
        status=post.status,
        chat_count=post.chat_count,
        like_count=post.like_count,
        create_at=post.create_at,
        deadline=post.deadline,
        title=post.title,
        tags=[tag.name for tag in post.tag]
    ) for post in posts]


def get_posts(db: Session, params: CursorParams):
    query = db.query(Post).order_by(Post.create_at.desc())
    return paginate(query, params, transformer=post_to_summary_response)


def get_post(post_id: int, db: Session) -> PostDetailResponse:
    try:
        db_post = db.query(Post).filter(post_id == Post.id).first()
        if db_post is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')
        post_detail = PostDetailResponse(
            contents=db_post.contents
        )
        return post_detail
    except SQLAlchemyError as e:
        raise HTTPException(e)


def create_post(db: Session, post: PostCreate) -> PostResponse:
    try:
        db_post = Post(
            author_id=post.author_id,
            title=post.title,
            contents=post.contents,
            deadline=post.deadline,
            max_member=post.max_member
        )
        db.add(db_post)

        tags = []
        for tag_name in post.tags:
            tag_name = tag_name.lower()
            if tag_name not in tags:
                tags.append(tag_name)

        for tag_name in tags:
            db_tag = db.query(Tag).filter(tag_name == Tag.name, post.category_id == Tag.category_id).first()
            if db_tag is None:
                db_tag = Tag(name=tag_name, category_id=post.category_id)
                db.add(db_tag)

            db_post.tag.append(db_tag)

        db_chatroom = Chatroom(chat_type="public")
        db_post.chatroom.append(db_chatroom)

        db.commit()

        return PostResponse(
            post_id=db_post.id,
            title=db_post.title,
            tags=[tag.name for tag in db_post.tag],
            author_id=db_post.author_id,
            create_at=db_post.create_at,
            like_count=db_post.like_count,
            current_member=db_post.current_member)
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def update_post(db: Session, post: PostUpdate, user_info: MemberCreate) -> PostResponse:
    try:
        permission = db.query(Post).filter_by(author_id=user_info["id"], id=post.id).first()
        if permission is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Have not permission')

        db_post = db.query(Post).filter_by(id=post.id).first()
        if db_post:
            db_post.title = post.title,
            db_post.contents = post.contents,
            db_post.deadLine = post.deadLine,
            db_post.max_member = post.max_member

        db.query(post_tag).filter_by(post_id=db_post.id).delete()

        tags = []
        for tag_name in post.tags:
            tag_name = tag_name.lower()
            if tag_name not in tags:
                tags.append(tag_name)

        for tag_name in tags:
            db_tag = db.query(Tag).filter(tag_name == Tag.name, post.category_id == Tag.category_id).first()
            if db_tag is None:
                db_tag = Tag(name=tag_name, category_id=post.category_id)
                db.add(db_tag)

            db_post.tag.append(db_tag)

        db.commit()

        return PostResponse(
            post_id=db_post.id,
            title=db_post.title,
            tags=[tag.name for tag in db_post.tag],
            author_id=db_post.author_id,
            create_at=db_post.create_at,
            like_count=db_post.like_count,
            current_member=db_post.current_member)
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def toggle_like_post(post_id: int, user_id: int, db: Session):
    try:
        db_post = db.query(Post).filter(post_id == Post.id).first()
        if db_post is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')

        like = db.query(Like).filter(post_id == Like.post_id, user_id == Like.user_id).first()

        if like:
            db_post.like_count -= 1
            db.delete(like)
            is_liked = False
        else:
            like = Like(user_id=user_id, post_id=post_id)
            db_post.like_count += 1
            db.add(like)
            is_liked = True
        db.commit()
        return LikeResponse(
            user_id=user_id,
            post_id=post_id,
            is_liked=is_liked
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def is_post_author(db: Session, post_id: int, member_id: int) -> bool:
    return db.query(Post).filter_by(id=post_id, author_id=member_id).first() is not None
