from typing import Sequence, Union
from api.models.model import Post, Tag, Like
from api.schemas.like import LikeResponse
from fastapi import HTTPException
from fastapi_pagination.cursor import CursorParams
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from api.schemas.post import PostCreate, PostSummaryResponse, PostDetailResponse, PostResponse
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
        tags=[tag.name for tag in post.tag],
        category_id=post.category_id
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
            category_id=post.category_id,
            title=post.title,
            contents=post.contents,
            deadline=post.deadline,
            max_member=post.max_member
        )
        db.add(db_post)

        for tag_name in post.tags:
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
