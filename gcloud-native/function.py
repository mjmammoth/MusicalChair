import os
import random
import json
from google.cloud import storage

from slack_bolt import App

STORAGE_CLIENT = storage.Client()
BUCKET_NAME = os.environ.get("GCP_BUCKET")
BUCKET = STORAGE_CLIENT.get_bucket(BUCKET_NAME)
CHANNEL_ID = os.environ.get("SLACK_CHANNEL_ID")
BLOB = BUCKET.blob('exclusions.json')

app = App()


def get_state():
    if not BLOB.exists():
        bot_id = app.client.auth_test()["user_id"]
        state = {'permanent_exclusions': [bot_id],
                 'already_asked': [],
                 'cached_week_day': None}
    else:
        state = json.loads(BLOB.download_as_string())
    return state


def generate_message(member_id):
    questions = [
        "Hey there, <@{}>! What's your daily dose of earworms today?",
        "<@{}> Are you gonna leave us hanging or are you gonna tell us your song of the day?",
        "Alright, <@{}> - spill the tea. What's the song that's been stuck in your head all day?",
        "Okay, <@{}>. You know the drill. What's the song that's making you feel all the feels?",
        "<@{}> We need your song of the day to keep us going, don't hold out on us!",
        "Yo, <@{}>! What's the tune that's been rocking your socks today?",
        "<@{}> It's not like we need your song of the day or anything... but we kinda do, so spill the beans!",
        "Hey <@{}> - just checking in, have you found a song that's better than yesterday's yet?",
        "<@{}> Don't keep us in suspense, what's the song that's been on repeat for you today?",
        "Okay <@{}>, it's time to share. What's your song of the day? We won't judge... much.",
        "<@{}> What's your song of the day?",
        "Hey <@{}>, have you been listening to anything good today? What's your song of the day?",
        "Good morning, <@{}>! Do you have a song of the day to share with us?",
    ]
    return random.choice(questions).format(member_id)


def ask_for_song(request):
    state = get_state()
    exclusions = state['permanent_exclusions'] + state['already_asked']
    channel = app.client.conversations_members(channel=CHANNEL_ID)
    channel_members = channel['members']
    remaining_pool = [uid for uid in channel_members
                      if uid not in exclusions]

    if not remaining_pool:
        remaining_pool = [uid for uid in channel_members
                          if uid not in state['permanent_exclusions']]
        state['already_asked'] = []

    member_id = random.choice(remaining_pool)
    message = generate_message(member_id)
    state['already_asked'].append(member_id)

    app.client.chat_postMessage(channel=CHANNEL_ID, text=message)
    BLOB.upload_from_string(json.dumps(state))
    return {'response': 200}
