from starlette.config import Config
import os

# 환경 변수를 로드할 .env 파일의 경로를 명시합니다.
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')

config = Config(env_path)


class Settings:
    SECRET_KEY: str = config('SECRET_KEY')
    KAKAO_CLIENT_ID: str = config('KAKAO_CLIENT_ID')
    KAKAO_CLIENT_SECRET: str = config('KAKAO_CLIENT_SECRET')


settings = Settings()
