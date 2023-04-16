import os
import textwrap

REQUIRED_ENV_VARS = [
    'SLACK_CHANNEL_ID',
    'SLACK_SIGNING_SECRET',
]

GOOGLE_ENV_VARS = [
    'GCP_REGION',
    'GCP_SERVICE_NAME',
]


def check_for_missing_vars(var_list):
    """Checks for missing environment variables and raises an error if any are missing"""
    missing_vars = []
    for var in var_list:
        if var not in os.environ:
            missing_vars.append(var)

    if missing_vars:
        error_message = f'''
            Missing required environment variables:
            {missing_vars}
        '''
        raise EnvironmentError(textwrap.dedent(error_message))


class BaseConfig():
    def __init__(self):
        check_for_missing_vars(REQUIRED_ENV_VARS)

    LOGGING_LEVEL = os.environ.get('LOGGING_LEVEL', 'INFO').upper()
    CHANNEL_ID = os.environ.get('SLACK_CHANNEL_ID')
    COLLECTION = os.environ.get('FIRESTORE_COLLECTION', 'musical-chair-slackbot')
    SONG_COLLECTION = os.environ.get('FIRESTORE_SONG_COLLECTION', 'musical-chair-slackbot-songs')
    SLACK_SIGNING_SECRET = os.environ.get('SLACK_SIGNING_SECRET')
    PORT = int(os.environ.get('PORT', '8000'))
    DEPLOYMENT_ENV = 'local'
    URL = os.environ.get('LOCAL_URL', f'http://127.0.0.1:{PORT}')
    SLACK_APP_CLIENT_ID = os.environ.get('SLACK_APP_CLIENT_ID')
    SLACK_APP_CLIENT_SECRET = os.environ.get('SLACK_APP_CLIENT_SECRET')


class GcpConfig(BaseConfig):
    def __init__(self, url):
        super().__init__()
        check_for_missing_vars(GOOGLE_ENV_VARS)
        self.URL = url

    REGION = os.getenv("GCP_REGION")
    SERVICE_NAME = os.getenv("GCP_SERVICE_NAME")
    DEPLOYMENT_ENV = 'GCP'


def get_env_vars():
    """Returns the correct config class based on the deployment environment"""
    deployment_env = os.environ.get('DEPLOYMENT_ENV', 'GCP').lower()
    if deployment_env == 'local':
        return BaseConfig
    else:
        from env.gcp.cloud_run_url import get_service_url
        url = get_service_url()
        return GcpConfig(url)


settings = get_env_vars()
