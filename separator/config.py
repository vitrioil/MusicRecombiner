import os
import secrets


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_urlsafe(16))
    SESSION_TYPE = os.environ.get("SESSION_TYPE", "filesystem")

