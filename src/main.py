import os
import random

import uvicorn
from fastapi import FastAPI, Request
from google.cloud import firestore
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler

from messages import generate_message
from service_url import get_service_url
from config import get_env_vars

settings = get_env_vars()

resp = get_service_url()
FIRESTORE_CLIENT = firestore.Client()
DOC_REF = FIRESTORE_CLIENT.collection(settings.COLLECTION).document('state')

slack_app = AsyncApp(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)
web_app = FastAPI()
handler = AsyncSlackRequestHandler(slack_app)


def get_state():
    state = DOC_REF.get()
    if not state.exists or state.to_dict()['already_asked'] is None:
        bot_id = slack_app.client.auth_test()["user_id"]
        state = {'permanent_exclusions': [bot_id],
                 'already_asked': []}
        DOC_REF.set(state)
    else:
        state = state.to_dict()
    return state


def get_remaining_pool(state):
    exclusions = state['permanent_exclusions'] + state['already_asked']
    channel = slack_app.client.conversations_members(channel=settings.CHANNEL_ID)
    channel_members = channel['members']
    remaining_pool = [uid for uid in channel_members
                      if uid not in exclusions]

    if not remaining_pool:
        remaining_pool = [uid for uid in channel_members
                          if uid not in state['permanent_exclusions']]
        state['already_asked'] = []
    return remaining_pool, state


@web_app.post("/ask-for-song", status_code=200)
def ask_for_song():
    state = get_state()
    remaining_pool, state = get_remaining_pool(state)
    member_id = random.choice(remaining_pool)
    message = generate_message(member_id)
    slack_app.client.chat_postMessage(channel=CHANNEL_ID, text=message)

    state['already_asked'].append(member_id)
    DOC_REF.set(state)
    return {'response': 200}


@web_app.post("/slack/events", status_code=200)
async def handle_slack_event(request: Request):
    # jsonbody = await request.json()
    # return jsonbody.get("challenge")

    response = await handler.handle(request)
    return response

    # Parse the incoming Slack event request
    # body = await request.body()
    # try:
    #     req = handler.async_handler.parse_request(body.decode("utf-8"))
    # except ValueError as e:
    #     return {"status": 400, "error": str(e)}
    #
    # # Handle the app_home_opened event
    # if req["type"] == "app_home_opened":
    #     user_id = req["event"]["user"]
    #     view = {
    #         "type": "home",
    #         "blocks": [
    #             {
    #                 "type": "section",
    #                 "text": {
    #                     "type": "plain_text",
    #                     "text": f"Welcome to your app home, <@{user_id}>!",
    #                 },
    #             },
    #         ],
    #     }
    #     try:
    #         # Publish a view to the user's app home tab
    #         print('FURK')
    #         await slack_app.client.views_publish(user_id=user_id, view=view)
    #     except SlackApiError as e:
    #         return {"status": 500, "error": str(e)}
    #
    # # Return a 200 response to Slack to acknowledge receipt of the event
    # return {"status": 200, "message": "Event received"}


@slack_app.event("app_mention")
async def handle_mention(event, say):
    await say("I received your message!")
    # channel_id = event["channel"]
    # user_id = event["user"]
    # text = event["text"]
    # await slack_app.client.reactions_add(
    #     channel=channel_id,
    #     timestamp=event["ts"],
    #     name="thumbsup"
    # )
    # await slack_app.client.chat_postmessage(
    #     channel=channel_id,
    #     text=f"hey <@{user_id}>! you said: {text}"
    # )


@slack_app.event("message")
async def handle_message(event, say):
    await say("I received your message!")
    # channel_id = event["channel"]
    # user_id = event["user"]
    # text = event["text"]
    # await slack_app.client.reactions_add(
    #     channel=channel_id,
    #     timestamp=event["ts"],
    #     name="thumbsup"
    # )
    # await slack_app.client.chat_postmessage(
    #     channel=channel_id,
    #     text=f"hey <@{user_id}>! you said: {text}"
    # )


@slack_app.event("app_home_opened")
async def update_home_tab(client, event, logger):
    user_id = event["user"]
    await client.views_publish(
        user_id=user_id,
        view={
            "type": "home",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "Musical Chair",
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Hello <@{user_id}>\n\nWelcome to the home page for the sometimes not-so-friendly music bot :musical_note::chair:"
                    }
                },
                {
                  "type": "image",
                  "image_url": "https://example.com/my-app-logo.png",
                  "alt_text": "My app logo"
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Opt-Out",
                                "emoji": True
                            },
                            "value": "click_me_123",
                            "url": "https://google.com"
                        }
                    ]
                }
            ]
        }
    )


if __name__ == "__main__":
    uvicorn.run(web_app, host="0.0.0.0", port=os.environ.get("PORT", 8000))
