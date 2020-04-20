import os
import secrets
from pathlib import Path


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_urlsafe(16))
    SESSION_TYPE = os.environ.get("SESSION_TYPE", "filesystem")
    AUDIO_PATH = Path("session_audio")

