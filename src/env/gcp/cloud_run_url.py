import os
import google.auth
from google.cloud import run_v2

from config import get_env_vars

settings = get_env_vars()

creds, project = google.auth.default()
REGION = settings.REGION
SERVICE_NAME = settings.SERVICE_NAME

client = run_v2.ServicesClient()
request = run_v2.GetServiceRequest(
    name=f"projects/{project}/locations/{REGION}/services/{SERVICE_NAME}"
)


def get_service_url():
    response = client.get_service(request=request)
    url = response.uri
    print(f'URL: {url}')
    return url