from app_instances import slack_app
from config import settings
from state_handler import state
from .ask_for_song_prompts import generate_prompt


async def ask_for_song():
    # remaining_pool = await state.get_remaining_pool()
    # member_id = random.choice(remaining_pool)
    member_id = await state.get_random_member_from_pool()
    message = generate_prompt(member_id)
    await slack_app.client.chat_postMessage(channel=settings.CHANNEL_ID,
                                            text=message)
    await state.add_user_to_already_asked(member_id)
