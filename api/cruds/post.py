from api.models.model import Post, Tag
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from api.schemas.post import PostCreate, PostResponse
from starlette import status


def get_posts(db: Session):
    db_post_list = db.query(Post).all()

    return [PostResponse(post_id=db_post.id,
                         title=db_post.title,
                         tags=[tag.name for tag in db_post.tag],
                         author_id=db_post.author_id,
                         create_at=db_post.create_at,
                         like_count=db_post.like_count,
                         current_member=db_post.current_member) for db_post in db_post_list]

def create_post(db: Session, post: PostCreate):
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
            db_tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if db_tag is None:
                db_tag = Tag(name=tag_name, use_count=1)
                db.add(db_tag)
            else:
                db_tag.use_count += 1

            db_post.tag.append(db_tag)

        db.commit()

        post_response = PostResponse(post_id=db_post.id,
                     title=db_post.title,
                     tags=[tag.name for tag in db_post.tag],
                     author_id=db_post.author_id,
                     create_at=db_post.create_at,
                     like_count=db_post.like_count,
                     current_member=db_post.current_member)

        return post_response
    except SQLAlchemyError as e:
        db.rollback()
        raise e