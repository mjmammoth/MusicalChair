from config import settings

if settings.DEPLOYMENT_ENV == 'local':
    from env.local.storage import FirestoreClientMock
    FIRESTORE_CLIENT = FirestoreClientMock()
else:
    from google.cloud import firestore
    FIRESTORE_CLIENT = firestore.Client()
