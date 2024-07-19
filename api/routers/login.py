from fastapi import APIRouter, Request, HTTPException, Depends
from starlette.responses import JSONResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from api.configs.app_config import settings
from api.cruds import member as crud_member
from api.db import get_db
from sqlalchemy.orm import Session

from api.schemas import login as login_schema


router = APIRouter(tags=["login"])

# OAuth 클라이언트 설정
oauth = OAuth()

# Kakao OAuth 설정
oauth.register(
    name='kakao',
    client_id=settings.KAKAO_CLIENT_ID,
    client_secret=settings.KAKAO_CLIENT_SECRET,
    # 인가 코드 받기 URL
    authorize_url='https://kauth.kakao.com/oauth/authorize',
    authorize_params=None,
    # 토큰 받기 URL
    access_token_url='https://kauth.kakao.com/oauth/token',
    access_token_params=None,
    client_kwargs={'token_endpoint_auth_method': 'client_secret_post'}
)


@router.get('/login/{provider}')
async def login(request: Request, provider: str):
    # 지원하지 않는 로그인 방식 예외 처리
    if provider not in oauth._clients:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    # 로그인 URI로 리다이렉트 응답
    redirect_uri = request.url_for('auth', provider=provider)
    return await oauth.create_client(provider).authorize_redirect(request, redirect_uri)


@router.get('/auth/{provider}/callback')
async def auth(request: Request, provider: str, db: Session = Depends(get_db)):
    try:
        if provider == 'kakao':
            # access 토큰 가져오기
            token_response = await oauth.kakao.authorize_access_token(request)
            access_token = token_response.get('access_token')
            if not access_token:
                raise HTTPException(status_code=401, detail="Invalid token")

            # 유저 정보 가져오기 (provider_type, provider_id, nickname)
            user_info = await crud_member.get_kakao_user_info(access_token)
            if not user_info:
                raise HTTPException(status_code=400, detail="Failed to retrieve user info")

        # 처음 로그인한 유저는 등록
        session_data = crud_member.find_member(db, user_info)
        if not session_data:
            session_data = crud_member.create_member(db=db, member_create=session_data)

        # 로그인한 유저 세션 저장소에 등록
        request.session['user'] = dict(session_data)

    except OAuthError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return JSONResponse({"message": "Login successful"})


@router.get('/logout')
async def logout(request: Request):
    # 로그아웃한 유저 세션 저장소에서 삭제
    logout_user = request.session.pop('user', None)
    if not logout_user:
        raise HTTPException(status_code=400, detail="Already logged out")

    return JSONResponse({"message": "Logout successful", "user":logout_user})
