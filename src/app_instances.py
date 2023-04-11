from fastapi import FastAPI
from slack_bolt.app.async_app import AsyncApp

from config import settings

# To avoid circular imports, we create the app instances here
slack_app = AsyncApp(
    token=settings.SLACK_BOT_TOKEN,
    signing_secret=settings.SLACK_SIGNING_SECRET,
)
web_app = FastAPI()
