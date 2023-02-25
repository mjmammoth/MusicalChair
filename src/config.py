import os
from functools import lru_cache


class BaseConfig:
    CHANNEL_ID = os.environ.get("SLACK_CHANNEL_ID")
    STATE_FILE: str = os.environ.get(
        'STATE_FILE', '/mnt/persistence/exclusions.json')
    MESSAGE_HOUR: int = int(os.environ.get('MESSAGE_HOUR', 10))
    SCHEDULE_TIMER: int = int(os.environ.get('SCHEDULE_TIMER', 60))
    LOGGING_LEVEL = os.environ.get('LOGGING_LEVEL', "INFO").upper()
    WEEKDAYS = (5
                if os.environ.get('WEEKDAYS_ONLY', "True") == "True"
                else 7)
    ONCE_A_DAY = (True
                  if os.environ.get('ONCE_A_DAY', "True") == "True"
                  else False)


@ lru_cache()
def get_settings():
    return BaseConfig()


settings = get_settings()
