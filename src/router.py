from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_sdk.web.async_client import AsyncWebClient

from app_instances import slack_app
from functions import backfill_playlists_process_messages, ask_for_song, get_bot_token_for_team


router = APIRouter()
handler = AsyncSlackRequestHandler(slack_app)


def get_slack_client(team_id):
    """Get the slack client for a team"""
    token = get_bot_token_for_team(team_id)
    return AsyncWebClient(token=token)


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


@router.post('/slack/commands', status_code=200)
async def route_handle_slack_commands(request: Request):
    """Handle Slack events"""
    response = await handler.handle(request)
    return response


@router.post('/ask-for-song', status_code=200)
async def route_ask_for_song(body: dict):
    """Ask for song, meant to be called from a cron job"""
    client = get_slack_client(body['team_id'])
    await ask_for_song(client)
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


@router.get('/slack/install')
async def install(request: Request):
    response = await handler.handle(request)
    return response


@router.get('/slack/oauth_redirect')
async def oauth(request: Request):
    response = await handler.handle(request)
    return response
