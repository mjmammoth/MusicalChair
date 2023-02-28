import os
import random
import json

import uvicorn
from fastapi import FastAPI, Request
from google.cloud import firestore
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler

from messages import generate_message

FIRESTORE_CLIENT = firestore.Client()
DOC_REF = FIRESTORE_CLIENT.collection('exclusions').document('state')
CHANNEL_ID = os.environ.get("SLACK_CHANNEL_ID")

slack_app = App()
web_app = FastAPI()
handler = SlackRequestHandler(slack_app)
web_app.mount("/events", handler)


def get_state():
    state = DOC_REF.get()
    if not state.exists:
        bot_id = slack_app.client.auth_test()["user_id"]
        state = {'permanent_exclusions': [bot_id],
                 'already_asked': []}
        DOC_REF.set(state)
    else:
        state = state.to_dict()
    return state


def get_remaining_pool(state):
    exclusions = state['permanent_exclusions'] + state['already_asked']
    channel = slack_app.client.conversations_members(channel=CHANNEL_ID)
    channel_members = channel['members']
    remaining_pool = [uid for uid in channel_members
                      if uid not in exclusions]

    if not remaining_pool:
        remaining_pool = [uid for uid in channel_members
                          if uid not in state['permanent_exclusions']]
        state['already_asked'] = []
    return remaining_pool, state


@web_app.post("/", status_code=200)
def ask_for_song():
    state = get_state()
    remaining_pool, state = get_remaining_pool(state)
    member_id = random.choice(remaining_pool)
    message = generate_message(member_id)
    slack_app.client.chat_postMessage(channel=CHANNEL_ID, text=message)

    state['already_asked'].append(member_id)
    DOC_REF.set(state)
    return {'response': 200}


@web_app.post("/events", status_code=200)
async def challenge(body: Request):
    jsonbody = await body.json()
    return jsonbody.get("challenge")

if __name__ == "__main__":
    uvicorn.run(web_app, host="0.0.0.0", port=os.environ.get("PORT", 8000))
