import os
import google.auth
from googleapiclient import discovery
from google.api_core.client_options import ClientOptions

creds, project = google.auth.default()
REGION = os.getenv("REGION")
SERVICE = os.getenv("SERVICE")
api_endpoint = f"https://{REGION}-run.googleapis.com"
options = ClientOptions(api_endpoint=api_endpoint)
service = discovery.build("run", "v1", client_options=options,
                          credentials=creds)
name = f"namespaces/{project}/services/{SERVICE}"
rqst = service.namespaces().services().get(name=name)
resp = rqst.execute()

def get_service_url():
    print(resp)
    print(resp['status']['url'])
    return resp
