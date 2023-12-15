from fastapi import Request


def get_access_token(request: Request):
    access_token = request.session.get("access_token")
    return access_token
