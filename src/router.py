import os

from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_sdk.errors import SlackApiError

from app_instances import slack_app
from functions import backfill_playlists_process_messages, ask_for_song

router = APIRouter()
handler = AsyncSlackRequestHandler(slack_app)


@router.post('/slack/events', status_code=200)
async def route_handle_slack_event(request: Request):
    """Handle Slack events"""
    response = await handler.handle(request)
    return response


@router.post('/slack/actions', status_code=200)
async def route_handle_action(request: Request):
    """Handle Slack actions ids"""
    response = await handler.handle(request)
    return response


@router.post('/ask-for-song', status_code=200)
async def route_ask_for_song():
    """Ask for song, meant to be called from a cron job"""
    await ask_for_song()
    return {'response': 200}


@router.post('/backfill-playlists', status_code=200)
async def route_backfill_playlists(background_tasks: BackgroundTasks):
    """
    Backfill playlists, meant to be a one time thing
    Asynchronously process messages in the background
    """
    background_tasks.add_task(backfill_playlists_process_messages)
    return {'response': 200}


@router.get('/header')
async def get_header_image():
    """
    Get the header image, used in the Slack app home page as images
    only work if the are available publicly.
    """
    return FileResponse('header.png')


installed_html = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <title>MusicalChair App Installed</title>
    <style>
      body {
        font-family: Arial, sans-serif;
        background-color: #f7f7f7;
      }
      .container {
        width: 100%;
        max-width: 800px;
        margin: 0 auto;
        padding: 40px;
        box-shadow: 0 0 10px rgba(0,0,0,0.3);
        border-radius: 5px;
        text-align: center;
      }
      h1 {
        font-size: 32px;
        font-weight: bold;
        margin-top: 0;
      }
      p {
        font-size: 16px;
        line-height: 1.5;
        margin-top: 20px;
      }
      a {
        color: #0070c9;
        text-decoration: none;
      }
      .emoji {
        font-size: 20px;
        margin-right: 10px;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <h1>MusicalChair App Installed!</h1>
      <p>Thank you for installing MusicalChair in your Slack workspace. <span class="emoji">🎵</span></p>
      <p>To use the app, simply type <code>/musicalchair</code> in any channel and follow the prompts.</p></p>
      <p>If you need help or have any questions, please visit our <a href="https://example.com/help">Help Center</a>. <span class="emoji">💬</span></p>
    </div>
  </body>
</html>
"""


@router.get('/slack/oauth', response_class=HTMLResponse)
async def oauth(request: Request):
    # Get the temporary authorization code from the request URL
    code = request.query_params.get('code')

    try:
        # Exchange the temporary code for an access token using the SlackClient instance
        response = await slack_app.client.oauth_v2_access(
            code=code,
            client_id=os.environ["SLACK_APP_CLIENT_ID"],
            client_secret=os.environ["SLACK_APP_CLIENT_SECRET"]
        )

        # Save the access token and other user-specific data in your app's database
        user_id = response['authed_user']['id']
        access_token = response['access_token']
        return installed_html
    except SlackApiError as e:
        return 'Error: {}'.format(e)
