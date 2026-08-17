
import os

from dotenv import load_dotenv
load_dotenv()

TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
TWITCH_BOT_ID = os.getenv("TWITCH_BOT_ID")

RIOT_API_KEY = os.getenv("RIOT_API_KEY")
AUTH_DOMAIN =os.getenv("AUTH_DOMAIN")