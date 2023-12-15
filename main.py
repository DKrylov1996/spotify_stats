from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from functions.functions import generate_random_string
from routers import auth, spotify_endpoints

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(SessionMiddleware, secret_key=generate_random_string())

app.include_router(auth.router)

app.include_router(spotify_endpoints.router)
