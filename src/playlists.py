import json

from config import get_env_vars
settings = get_env_vars()

if settings.DEPLOYMENT_ENV == 'local':
    from storage import LocalBucket
    bucket = LocalBucket()
else:
    from google.cloud import storage
    client = storage.Client()
    bucket = client.get_bucket(settings.BUCKET)


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


def handle_url(url):
    if 'spotify' in url:
        update_playlist_blob(url, 'spotify')
    elif 'youtube' in url:
        update_playlist_blob(url, 'youtube')
