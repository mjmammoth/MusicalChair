from fastapi import FastAPI
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler

from config import get_env_vars

settings = get_env_vars()

slack_app = AsyncApp(
    token=settings.SLACK_BOT_TOKEN,
    signing_secret=settings.SLACK_SIGNING_SECRET,
)
web_app = FastAPI()
handler = AsyncSlackRequestHandler(slack_app)
