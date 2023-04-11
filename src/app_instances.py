import os

from fastapi import FastAPI
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.oauth.async_oauth_settings import AsyncOAuthSettings

from config import settings

oauth_settings = AsyncOAuthSettings(
    client_id=os.environ["SLACK_APP_CLIENT_ID"],
    client_secret=os.environ["SLACK_APP_CLIENT_SECRET"],
    scopes=os.environ["SLACK_APP_SCOPE"].split(','),
    redirect_uri=os.environ["SLACK_APP_REDIRECT_URI"]
)

# To avoid circular imports, we create the app instances here
slack_app = AsyncApp(
    token=settings.SLACK_BOT_TOKEN,
    signing_secret=settings.SLACK_SIGNING_SECRET,
    oauth_settings=oauth_settings
)
web_app = FastAPI()
