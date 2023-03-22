from fastapi import APIRouter
from features import ask_for_song_router, playlist_router
from slack_events import event_handler_router

router = APIRouter()

router.include_router(ask_for_song_router)
router.include_router(playlist_router)
router.include_router(event_handler_router)