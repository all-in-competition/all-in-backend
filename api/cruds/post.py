from api.models.model import Post, Tag
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from api.schemas.post import PostCreate, PostSummaryResponse
from starlette import status


def get_posts(db: Session):
    db_post_list = db.query(Post).order_by(Post.create_at.desc()).all()
    a = Post()
    [db_tag for db_tag in a.tag]
    return [PostSummaryResponse(
        author_name=db_post.member.nickname,
        status=db_post.status,
        chat_count=db_post.chat_count,
        like_count=db_post.like_count,
        create_at=db_post.create_at,
        deadline=db_post.deadline,
        title=db_post.title,
        tags=[db_tag.name for db_tag in db_post.tag],
        category_id = db_post.category_id
    ) for db_post in db_post_list]

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