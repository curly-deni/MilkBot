from os import getenv
from datetime import datetime

current_year = datetime.now().year

__all__ = [
    "STARTUP_MESSAGE",
    "IS_SHARED",
    "STANDARD_PREFIX",
    "FILE_LOGGING",
    "DEBUG",
    "DISCORD_TOKEN",
]

STARTUP_MESSAGE = f"""MilkBot (v6) - Alpha
Copyright (c) 2021-{current_year} curly_deni (danila@dan-mi.ru)"""

IS_SHARED = False
STANDARD_PREFIX = "="

FILE_LOGGING = False
DEBUG = True

DISCORD_TOKEN = getenv("DISCORD_TOKEN")
