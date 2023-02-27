import os
import random
import json

import uvicorn
from fastapi import FastAPI
from google.cloud import storage
from slack_bolt import App

from messages import generate_message

STORAGE_CLIENT = storage.Client()
BUCKET_NAME = os.environ.get("GCP_BUCKET")
BUCKET = STORAGE_CLIENT.get_bucket(BUCKET_NAME)
CHANNEL_ID = os.environ.get("SLACK_CHANNEL_ID")
BLOB = BUCKET.blob("exclusions.json")

slack_app = App()
web_app = FastAPI()


def get_state():
    if not BLOB.exists():
        bot_id = slack_app.client.auth_test()["user_id"]
        state = {'permanent_exclusions': [bot_id],
                 'already_asked': [],
                 'cached_week_day': None}
    else:
        state = json.loads(BLOB.download_as_string())
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
    BLOB.upload_from_string(json.dumps(state))
    return {'response': 200}


if __name__ == "__main__":
    uvicorn.run(web_app, host="0.0.0.0", port=os.environ.get("PORT", 8000))
