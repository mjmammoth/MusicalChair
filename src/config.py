import os

REQUIRED_ENV_VARS = [
    'CHANNEL_ID',
    'SLACK_BOT_TOKEN',
    'SLACK_SIGNING_SECRET',
    'ENV_VAR_3',
    'DEPLOYMENT_ENV'
]

deployment_env = os.environ['DEPLOYMENT_ENV'].lower()

match deployment_env:
    case 'gcp':
        REQUIRED_ENV_VARS.append('FIRESTORE_COLLECTION')
    case 'local':
        REQUIRED_ENV_VARS.append('STATE_FOLDER')


class BaseConfig:
    CHANNEL_ID = os.environ.get("SLACK_CHANNEL_ID")
    STATE_FILE: str = os.environ.get(
        'STATE_FILE', '/mnt/persistence/exclusions.json')
    SCHEDULE_TIMER: int = int(os.environ.get('SCHEDULE_TIMER', 60))
    LOGGING_LEVEL = os.environ.get('LOGGING_LEVEL', "INFO").upper()
    CHANNEL_ID = os.environ.get("SLACK_CHANNEL_ID")
    COLLECTION = os.environ.get("FIRESTORE_COLLECTION", "musical-chair-slackbot")
    SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN"),
    SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET"),


def get_env_vars():
    missing_vars = []
    for var in REQUIRED_ENV_VARS:
        if var not in os.environ:
            missing_vars.append(var)


    if missing_vars:
        raise EnvironmentError(f'''Missing required environment
                               variable list: {missing_vars}''')

    return BaseConfig
