import os
import google.auth
from google.cloud import run_v2

# Not using config/settings to avoid circular import
REGION = os.getenv('GCP_REGION', 'europe-west2')
SERVICE_NAME = os.getenv('GCP_SERVICE_NAME', 'musical-chair-cr')

creds, project = google.auth.default()

client = run_v2.ServicesClient()
request = run_v2.GetServiceRequest(
    name=f'projects/{project}/locations/{REGION}/services/{SERVICE_NAME}'
)


def get_service_url():
    response = client.get_service(request=request)
    url = response.uri
    print(f'URL: {url}')
    return url
