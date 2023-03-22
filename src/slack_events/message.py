import re
from features import handle_song_url
from app_instances import slack_app

@slack_app.event('message')
async def handle_message(event):
    # TODO: Ignore messages from bot
    if event.get('subtype', None) != 'message_changed':
        urls = re.findall(r'(https?://\S[^>]+)', event.get('text', ''))
        for url in urls:
            handle_song_url(url)