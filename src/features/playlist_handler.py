import json
import re

from fastapi import APIRouter

from config import settings
from app_instances import slack_app
from storage import bucket, FIRESTORE_CLIENT

router = APIRouter()
SONG_COLLECTION = FIRESTORE_CLIENT.collection(settings.SONG_COLLECTION)


def update_playlist_blob(url, platform):
    blob = bucket.blob(f'{platform}_playlist')

    if blob.exists():
        playlist = blob.download_as_string()
        playlist = json.loads(playlist)
    else:
        playlist = []
    playlist.append(url)
    playlist = [*set(playlist)]
    blob.upload_from_string(json.dumps(playlist))


def add_song_to_firestore(song_data):
    # Check if the song already exists in the Firestore collection
    query = SONG_COLLECTION.where('youtube_url', '==', song_data['youtube_url']).where('spotify_url', '==', song_data['spotify_url']).get()

    if query:
        # If the song exists, update the 'posts' array with the new post
        song_ref = query[0].reference
        song_ref.update({
            'posts': firestore.ArrayUnion([song_data['posts'][0]])
        })
    else:
        # If the song does not exist, create a new document in the collection
        SONG_COLLECTION.add(song_data)


def handle_song_url(url, event):
    song_data = {
        "original_source": "youtube" if "youtube" in url else "spotify",
        "youtube_url": url if "youtube" in url else "",
        "spotify_url": url if "spotify" in url else "",
        "metadata": {
            "genre": [],
            "artist": "",
            "song_name": "",
            "album": ""
        },
        "posts": [
            {
                "date": event.get('ts', ''),
                "user_id": event.get('user', '')
            }
        ]
    }
    add_song_to_firestore(song_data)


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
