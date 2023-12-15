import random
import string
import requests

from fastapi import Request

from routers.auth import token_func


def generate_random_string(length=12):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def get_top_tracks_uris(request: Request, time_range="long_term"):
    time_range_dict = {"short_term": "last 4 weeks", "medium_term": "last 6 months", "long_term": "all time"}
    access_token = request.session.get("access_token")
    if access_token:

        r = requests.get(f"https://api.spotify.com/v1/me/top/tracks?time_range={time_range}&limit=50",
                         headers=token_func(request))
        response_data = r.json()
        tracks_uris = []
        for i in range(len(response_data["items"])):
            tracks_uris.append(response_data["items"][i]["uri"])
        track_uris_dict = {"uris": tracks_uris}
        return track_uris_dict
