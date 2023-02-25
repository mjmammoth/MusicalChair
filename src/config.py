import os
from functools import lru_cache


class BaseConfig:
    CHANNEL_ID = os.environ.get("SLACK_CHANNEL_ID")
    EXCLUSIONS_FILE: str = os.environ.get(
        'EXCLUSIONS_FILE', '/mnt/persistence/exclusions.json')

    if os.environ.get('WEEKDAYS_ONLY', True):
        DAYS_OF_WEEK = 5
    else:
        DAYS_OF_WEEK = 7

    MESSAGE_HOUR: int = os.environ.get('MESSAGE_HOUR', 10)
    SCHEDULE_TIMER: int = os.environ.get('SCHEDULE_TIMER', 60)


@ lru_cache()
def get_settings():
    return BaseConfig()


settings = get_settings()
