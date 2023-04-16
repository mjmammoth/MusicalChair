import os

from fastapi import FastAPI
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.oauth.async_oauth_settings import AsyncOAuthSettings

from config import settings
from slack_installation_firestore import FirestoreInstallationStore


oauth_settings = AsyncOAuthSettings(
    client_id=os.environ['SLACK_APP_CLIENT_ID'],
    client_secret=os.environ['SLACK_APP_CLIENT_SECRET'],
    scopes=os.environ['SLACK_APP_SCOPE'].split(','),
    installation_store=FirestoreInstallationStore()
)

# To avoid circular imports, we create the app instances here
slack_app = AsyncApp(
    signing_secret=settings.SLACK_SIGNING_SECRET,
    oauth_settings=oauth_settings
)
web_app = FastAPI()
