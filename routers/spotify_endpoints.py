import requests
from collections import Counter
from datetime import datetime
from urllib.parse import urlparse, parse_qs

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from routers.auth import token_func
from dependencies import get_access_token
from functions.functions import get_top_tracks_uris

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/")
async def main(request: Request, access_token: str = Depends(get_access_token)):
    if access_token:
        return templates.TemplateResponse("logged_in.html", {"request": request})
    else:
        return templates.TemplateResponse("not_logged_in.html", {"request": request})


@router.get("/top_artists", response_class=HTMLResponse)
def get_top_artists(request: Request, time_range="long_term", access_token: str = Depends(get_access_token)):
    time_range_dict = {"short_term": "last 4 weeks", "medium_term": "last 6 months", "long_term": "all time"}
    if access_token:

        def top_artists_info(time_range):
            r = requests.get(f"https://api.spotify.com/v1/me/top/artists?time_range={time_range}&limit=50",
                             headers=token_func(request))
            response_data = r.json()
            artists = []
            for i in range(len(response_data["items"])):
                artist_dict = {"place": (str(i + 1) + "."), "name": response_data["items"][i]["name"],
                               "url": response_data["items"][i]["external_urls"]["spotify"],
                               "img": response_data["items"][i]["images"][1]["url"]}
                artists.append(artist_dict)
            return artists

        return templates.TemplateResponse("top_artists.html",
                                          {"request": request,
                                           "artists": top_artists_info(time_range),
                                           "time_range_dict": time_range_dict,
                                           "time_range": time_range})
    else:
        return RedirectResponse(url="/auth/login")


@router.get("/top_tracks", response_class=HTMLResponse)
def get_top_tracks(request: Request, time_range="long_term", access_token: str = Depends(get_access_token)):
    time_range_dict = {"short_term": "last 4 weeks", "medium_term": "last 6 months", "long_term": "all time"}
    if access_token:
        def top_tracks_info(time_range):
            request.session["url"] = request.url.__str__()
            r = requests.get(f"https://api.spotify.com/v1/me/top/tracks?time_range={time_range}&limit=50",
                             headers=token_func(request))
            response_data = r.json()
            tracks = []
            for i in range(len(response_data["items"])):
                tracks_dict = {"place": (str(i + 1) + "."), "track_name": response_data["items"][i]["name"],
                               "artist_name": response_data["items"][i]["artists"][0]["name"],
                               "url": response_data["items"][i]["external_urls"]["spotify"],
                               "img": response_data["items"][i]["album"]["images"][2]["url"]}
                tracks.append(tracks_dict)
            return tracks

        return templates.TemplateResponse("top_tracks.html",
                                          {"request": request,
                                           "tracks": top_tracks_info(time_range),
                                           "time_range_dict": time_range_dict,
                                           "time_range": time_range})
    else:
        return RedirectResponse(url="/auth/login")


@router.get("/top_genres", response_class=HTMLResponse)
def get_top_genres(request: Request, time_range="long_term", access_token: str = Depends(get_access_token)):
    time_range_dict = {"short_term": "last 4 weeks", "medium_term": "last 6 months", "long_term": "all time"}
    if access_token:

        def top_genres_info(time_range):
            r = requests.get(f"https://api.spotify.com/v1/me/top/artists?time_range={time_range}&limit=50",
                             headers=token_func(request))
            response_data = r.json()
            genres = []
            for i in range(len(response_data["items"])):
                for j in range(len(response_data["items"][i]["genres"])):
                    item = response_data["items"][i]["genres"]
                    for genre in item:
                        genres.append(genre)
            element_counts = Counter(genres)
            top_ten = element_counts.most_common(10)
            return top_ten

        return templates.TemplateResponse("top_genres.html",
                                          {"request": request,
                                           "genres": top_genres_info(time_range),
                                           "time_range_dict": time_range_dict,
                                           "time_range": time_range})
    else:
        return RedirectResponse(url="/auth/login")


@router.get("/recently_played", response_class=HTMLResponse)
def get_recent_tracks(request: Request, access_token: str = Depends(get_access_token)):
    if access_token:
        r = requests.get(f"https://api.spotify.com/v1/me/player/recently-played?limit=50",
                         headers=token_func(request))
        response_data = r.json()
        play_info = []
        for i in range(len(response_data["items"])):
            original_date_string = response_data["items"][i]["played_at"]

            original_date = datetime.strptime(original_date_string, '%Y-%m-%dT%H:%M:%S.%fZ')

            formatted_date_string = original_date.strftime('%d.%m.%y, %H:%M')
            plays_dict = {"track_name": response_data["items"][i]["track"]["name"],
                          "artist_name": response_data["items"][i]["track"]["artists"][0]["name"],
                          "url": response_data["items"][i]["track"]["external_urls"]["spotify"],
                          "played_at": formatted_date_string}
            play_info.append(plays_dict)
        return templates.TemplateResponse("recently_played.html", {"request": request, "play_info": play_info})
    else:
        return RedirectResponse(url="/auth/login")


@router.get("/create_playlist")
def create_playlist(request: Request, access_token: str = Depends(get_access_token)):
    time_range_dict = {"short_term": "last 4 weeks", "medium_term": "last 6 months", "long_term": "all time"}
    if access_token:
        def get_user_id():
            r = requests.get(f"https://api.spotify.com/v1/me",
                             headers=token_func(request))
            response_data = r.json()
            return response_data["id"]

        url = f"https://api.spotify.com/v1/users/{get_user_id()}/playlists"
        parsed_url = urlparse(request.session.get("url"))
        query_params = parse_qs(parsed_url.query)
        time_range = query_params.get("time_range")
        if time_range is None:
            time_range = ["long_term"]
        r = requests.post(url,
                          json={
                              "name": f"Top Tracks {datetime.now().date().strftime('%d.%m.%y')} ({time_range_dict[time_range[0]]})",
                              "description": f"Your {time_range_dict[time_range[0]]} favorite tracks"},
                          headers=token_func(request))
        if r.status_code == 201:
            playlist_id = r.json()["id"]
            playlist_link = r.json()["external_urls"]["spotify"]

            requests.post(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
                          json=get_top_tracks_uris(request, time_range[0]), headers=token_func(request))
            return {"playlist_link": playlist_link}
        else:
            raise HTTPException(status_code=r.status_code,
                                detail=r.json())


@router.get("/logout")
def logout(request: Request):
    session = request.session
    session.clear()
    return RedirectResponse("/")
