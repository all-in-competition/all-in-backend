from fastapi import APIRouter
from fastapi.responses import RedirectResponse
import httpx
from dotenv import load_dotenv
import os

load_dotenv()
KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")
KAKAO_AUTH_URL = os.getenv("KAKAO_AUTH_URL")
KAKAO_TOKEN_URL = os.getenv("KAKAO_TOKEN_URL")
KAKAO_USER_URL = os.getenv("KAKAO_USER_URL")

router = APIRouter()


@router.get("/login")
async def kakao_login():
  authorize_url = 	f"https://kauth.kakao.com/oauth/authorize?client_id={KAKAO_CLIENT_ID}&redirect_uri={KAKAO_REDIRECT_URI}&response_type=code"
  return RedirectResponse(authorize_url)
  
@router.get("/oauth")
async def kakao_callback(code: str):
  # token_url = KAKAO_TOKEN_URL
  token_url = KAKAO_TOKEN_URL
  data = {
      "grant_type" : "authorization_code",
      "client_id" : KAKAO_CLIENT_ID,
      "redirect_url" : KAKAO_REDIRECT_URI,
      "code" : code
  }
  async with httpx.AsyncClient() as client:
      response = await client.post(url=token_url, data=data, headers = {"Content-type" : "application/x-www-form-urlencoded;charset=utf-8"})
      response_data = response.json()
      
      user_url = "https://kapi.kakao.com/v2/user/me"
      headers = {
        "Authorization" : f"Bearer {response_data['access_token']}",
        "Content-type" : "application/x-www-form-urlencoded;charset=utf-8",
      }
      
  async with httpx.AsyncClient() as client:
      user_response = await client.post(user_url, headers=headers)
      user_data = user_response.json()
      return {"user_data" : user_data}