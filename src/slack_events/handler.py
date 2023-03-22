from fastapi import APIRouter, Request
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from app_instances import slack_app

router = APIRouter()
handler = AsyncSlackRequestHandler(slack_app)

@router.post('/slack/events', status_code=200)
async def handle_slack_event(request: Request):
    response = await handler.handle(request)
    return response