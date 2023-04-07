import re

from google.cloud import firestore

from config import settings
from app_instances import slack_app
from storage import FIRESTORE_CLIENT

SONG_COLLECTION = FIRESTORE_CLIENT.collection(settings.SONG_COLLECTION)


def add_song_to_firestore(song_data):
    # Check if the song already exists in the Firestore collection
    query = (
                SONG_COLLECTION
                .where('youtube_url', '==', song_data['youtube_url'])
                .where('spotify_url', '==', song_data['spotify_url'])
                .get()
            )

    if len(query) > 0:
        # If the song exists, update the 'posts' array with the new post
        song_ref = query[0].reference
        song_ref.update({
            'posts': firestore.ArrayUnion([song_data['posts'][0]])
        })
    else:
        # If the song does not exist, create a new document in the collection
        SONG_COLLECTION.add(song_data)


def handle_media_url(url, event):
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


async def backfill_playlists_process_messages():
    messages = []
    next_cursor = None

    print("Starting backfilling media data...")
    print("Getting all messages from the channel...")
    while True:
        result = await slack_app.client.conversations_history(
            channel=settings.CHANNEL_ID,
            cursor=next_cursor
        )
        messages.extend(result['messages'])
        next_cursor = result.get('response_metadata', {}).get('next_cursor')
        if not next_cursor:
            break

    counter = 0
    bot_id = await slack_app.client.auth_test()
    url_pattern = re.compile(r'(https?://\S[^>]+)')

    print("Processing messages...")
    for message in messages:
        # Skip messages from the bot
        if message.get('user') == bot_id['user_id']:
            continue

        urls = url_pattern.findall(message.get('text', ''))

        for url in urls:
            if 'youtube' in url or 'spotify' in url:
                counter += 1
                handle_media_url(url, message)

    print('Done backfilling media data!')
    print(f'Added {counter} songs to the Firestore collection')
