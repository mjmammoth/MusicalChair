import random
from fastapi import APIRouter
from fastapi import Depends, HTTPException, Header
from google.oauth2 import id_token
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
import os

from config import settings
from .prompt_questions import generate_prompt
from storage import FIRESTORE_CLIENT
from app_instances import slack_app

router = APIRouter()
DOC_REF = FIRESTORE_CLIENT.collection(settings.COLLECTION).document('state')

GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

client_config = {
    "web": {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "redirect_uris": ["http://localhost:8000/auth_callback"],
    }
}

oauth2_flow = Flow.from_client_config(
    client_config=client_config,
    scopes=["openid", "email", "profile"],
    redirect_uri="http://localhost:8000/auth_callback",
)


async def verify_google_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header is missing")

    try:
        token = authorization.split(" ")[1]
        idinfo = id_token.verify_oauth2_token(token, Request(), GOOGLE_CLIENT_ID)

        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            raise ValueError("Wrong issuer")

        return idinfo["sub"]

    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_state():
    state = DOC_REF.get()
    if not state.exists or state.to_dict()['already_asked'] is None:
        bot_id = await slack_app.client.auth_test()
        bot_id = bot_id['user_id']
        state = {'permanent_exclusions': [bot_id],
                 'already_asked': []}
        DOC_REF.set(state)
    else:
        state = state.to_dict()
    return state


async def get_remaining_pool(state):
    exclusions = state['permanent_exclusions'] + state['already_asked']
    channel = await slack_app.client.conversations_members(
        channel=settings.CHANNEL_ID
    )
    channel_members = channel['members']
    remaining_pool = [uid for uid in channel_members
                      if uid not in exclusions]

    if not remaining_pool:
        remaining_pool = [uid for uid in channel_members
                          if uid not in state['permanent_exclusions']]
        state['already_asked'] = []
    return remaining_pool, state


@router.post('/ask-for-song', status_code=200)
async def ask_for_song(user_id: str = Depends(verify_google_token)):
    state = await get_state()
    remaining_pool, state = await get_remaining_pool(state)
    member_id = random.choice(remaining_pool)
    message = generate_prompt(member_id)
    await slack_app.client.chat_postMessage(channel=settings.CHANNEL_ID,
                                            text=message)

    state['already_asked'].append(member_id)
    DOC_REF.set(state)
    return {'response': 200}
