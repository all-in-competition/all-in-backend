from fastapi import APIRouter, Request, HTTPException, Depends
from starlette.responses import JSONResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from api.configs.app_config import settings
from aiohttp import ClientSession
from api.cruds import member
from api.db import get_db
from sqlalchemy.orm import Session

from api.schemas.login import SessionData, to_session_data


router = APIRouter()

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
    if provider not in oauth._clients:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    redirect_uri = request.url_for('auth', provider=provider)
    return await oauth.create_client(provider).authorize_redirect(request, redirect_uri)


def is_first_login(db: Session, session_data: SessionData) -> bool:
    find_user = member.find_member(db=db, user_info=session_data)
    if find_user:
        return True
    else:
        return False


async def get_kakao_user_info(token):
    user_info_url = "https://kapi.kakao.com/v2/user/me"
    headers = {"Authorization": f"Bearer {token}"}

    async with ClientSession() as client:
        async with client.get(user_info_url, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail="Failed to fetch user info from Kakao")
            user_info = await response.json()
    return user_info


@router.get('/auth/{provider}/callback')
async def auth(request: Request, provider: str, db: Session = Depends(get_db)):
    try:
        if provider == 'kakao':
            token = await oauth.kakao.authorize_access_token(request)
            user_info = await get_kakao_user_info(token.get('access_token'))
            session_data = to_session_data(user_info)
            if is_first_login(db=db, session_data=session_data):
                member.create_member(db=db, member_create=session_data)

        if not session_data:
            raise HTTPException(status_code=400, detail="Failed to retrieve user info")

        request.session['user'] = dict(session_data)
    except OAuthError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return JSONResponse({"message": "Login successful"})


@router.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return JSONResponse({"message": "Logout successful"})
