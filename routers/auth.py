import base64
import requests

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse

from config import CLIENT_ID, REDIRECT_URI, CLIENT_SECRET

router = APIRouter(
    prefix="/auth"
)


@router.get("/login")
def login(request: Request):
    # Перенаправляем пользователя на страницу авторизации Spotify
    spotify_url = f"https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope=user-top-read%20user-read-private%20user-read-recently-played%20user-read-email%20playlist-modify-public%20playlist-modify-private&show_dialog=False"
    return RedirectResponse(url=spotify_url)


@router.get("/callback")
async def process_callback(request: Request, code: str = None):
    if code:
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
        token_response = requests.post("https://accounts.spotify.com/api/token", data=token_data)

        if token_response.status_code == 200:
            token_info = token_response.json()
            access_token = token_info["access_token"]
            refresh_token = token_info["refresh_token"]

            # Сохраняем полученные access token и refresh token в сессии
            request.session["access_token"] = access_token
            request.session["refresh_token"] = refresh_token
            return RedirectResponse(url="/", status_code=302)
        else:
            raise HTTPException(status_code=401, detail="Не удалось получить токены авторизации")
    else:
        raise HTTPException(status_code=400, detail="Отсутствует код авторизации в запросе")


def token_func(request):
    new_token_data = {
        "grant_type": "refresh_token",
        "refresh_token": request.session.get("refresh_token"),
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f'Basic {base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode("utf-8")).decode("utf-8")}'
    }
    new_token_response = requests.post("https://accounts.spotify.com/api/token", data=new_token_data,
                                       headers=headers)
    if new_token_response.status_code == 200:
        new_access_token = new_token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {new_access_token}"}
        return headers
