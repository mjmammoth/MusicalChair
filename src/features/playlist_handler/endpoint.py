import json
import re

from fastapi import APIRouter

from config import get_env_vars
from app_instances import slack_app
from storage import bucket

settings = get_env_vars()
router = APIRouter()


def update_playlist_blob(url, platform):
    blob = bucket.get_blob(f'{platform}_playlist')
    if not blob:
        blob = bucket.blob(f'{platform}_playlist')

    playlist = blob.download_as_string()
    if playlist:
        playlist = json.loads(playlist)
    else:
        playlist = []
    playlist.append(url)
    playlist = [*set(playlist)]
    blob.upload_from_string(json.dumps(playlist))


def handle_song_url(url):
    if 'spotify' in url:
        update_playlist_blob(url, 'spotify')
    elif 'youtube' in url:
        update_playlist_blob(url, 'youtube')

@router.post('/backfill-playlists', status_code=200)
async def backfill_playlists():
    result = await slack_app.client.conversations_history(
        channel=settings.CHANNEL_ID)
    messages = result["messages"]
    urls = []
    for message in messages:
        urls.extend(re.findall(r'(https?://\S[^>]+)', message.get('text', '')))

    for url in urls:
        handle_song_url(url)
    return {'response': 200}