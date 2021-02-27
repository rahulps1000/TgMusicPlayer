from os import environ


SESSION_NAME = environ.get("SESSION_NAME", "session")
BOT_TOKEN = environ.get("BOT_TOKEN")

API_ID = int(environ.get("API_ID"))
API_HASH = environ.get("API_HASH")

DURATION_LIMIT = int(environ.get("DURATION_LIMIT", "7"))

SUDO_USERS = list(map(int, environ.get("SUDO_USERS").split()))
