from config import settings
from state_handler import SongOfTheDayStateHandler
from .ask_for_song_prompts import generate_prompt


async def ask_for_song(client):
    """Ask for song, meant to be called from a cron job"""
    sotd_state = SongOfTheDayStateHandler(client)
    member_id = await sotd_state.get_random_member_from_pool()
    message = generate_prompt(member_id)
    await client.chat_postMessage(channel=settings.CHANNEL_ID,
                                  text=message)
    await sotd_state.add_user_to_already_asked(member_id)
