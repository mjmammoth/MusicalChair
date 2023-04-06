import re
from features import handle_song_url
from app_instances import slack_app


@slack_app.event('message')
async def handle_message(event):
    # Ignore messages from bot itself
    bot_id = await slack_app.client.auth_test()
    if event.get('user', None) == bot_id['user_id']:
        return

    if event.get('subtype', None) != 'message_changed':
        urls = re.findall(r'(https?://\S[^>]+)', event.get('text', ''))
        for url in urls:
            handle_song_url(url, event)
