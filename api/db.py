from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_URL = "mysql+pymysql://root@db:3306/demo?charset=utf8"

#데이터베이스 연결과 관리을 위한 Engine 객체생성
db_engine = create_engine(DB_URL, echo=True)

#db_engine을 이용하여 Session 객체를 생성
db_session = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


Base = declarative_base()

def get_db():
  with db_session() as session:
    yield session
