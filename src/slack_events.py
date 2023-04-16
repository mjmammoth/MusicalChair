import re

from app_instances import slack_app
from functions import publish_home_view, handle_media_url


@slack_app.event('app_home_opened')
async def update_home_tab(client, event, logger):
    user_id = event['user']
    await publish_home_view(user_id, client)


@slack_app.event('message')
async def handle_message(event):
    if event.get('subtype', None) != 'message_changed':
        urls = re.findall(r'(https?://\S[^>]+)', event.get('text', ''))
        for url in urls:
            handle_media_url(url, event)


@slack_app.event('app_mention')
async def handle_mention(event, say):
    await say('I received your message!')
