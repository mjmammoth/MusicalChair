import random
from fastapi import APIRouter

from config import get_env_vars
from .prompt_questions import generate_prompt
from storage import DOC_REF
from app_instances import slack_app

settings = get_env_vars()
router = APIRouter()

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
async def ask_for_song():
    state = await get_state()
    remaining_pool, state = await get_remaining_pool(state)
    member_id = random.choice(remaining_pool)
    message = generate_prompt(member_id)
    await slack_app.client.chat_postMessage(channel=settings.CHANNEL_ID,
                                            text=message)

    state['already_asked'].append(member_id)
    DOC_REF.set(state)
    return {'response': 200}