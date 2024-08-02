from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from api.configs.app_config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

DB_URL = settings.DB_URL
DB_URL_ASYNC = settings.DB_URL_ASYNC

engine_async = create_async_engine(DB_URL_ASYNC, echo=True)


async_session = async_sessionmaker(
    bind=engine_async
)



#데이터베이스 연결과 관리을 위한 Engine 객체생성
db_engine = create_engine(DB_URL, echo=True)

#db_engine을 이용하여 Session 객체를 생성
db_session = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


Base = declarative_base()

def get_db():
  db = db_session()
  try:
    yield db
  finally:
    db.close()



async def get_db_async() -> AsyncSession:
  async with async_session() as session:
    yield session


