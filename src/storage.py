from config import settings

if settings.DEPLOYMENT_ENV == 'local':
    from env.local.storage import LocalFirestore
    DOC_REF = LocalFirestore()
else:
    from google.cloud import firestore
    FIRESTORE_CLIENT = firestore.Client()
