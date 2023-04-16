
from slack_sdk.oauth.installation_store.async_installation_store import AsyncInstallationStore
from slack_sdk.oauth.installation_store.models.installation import Installation
from storage import FIRESTORE_CLIENT


class FirestoreInstallationStore(AsyncInstallationStore):
    def __init__(self):
        super().__init__()
        self.db = FIRESTORE_CLIENT

    async def async_save(self, installation):
        doc_ref = self.db.collection(
            'installations').document(installation.team_id)
        doc_ref.set(installation.__dict__)

    async def async_find_installation(
        self, *,
        enterprise_id: str = None, team_id: str = None, user_id: str = None,
        is_enterprise_install: bool = None
    ):
        doc_ref = self.db.collection('installations')
        if enterprise_id is not None:
            doc_ref = doc_ref.where('enterprise_id', '==', enterprise_id)
        if team_id is not None:
            doc_ref = doc_ref.where('team_id', '==', team_id)
        if user_id is not None:
            doc_ref = doc_ref.where('user_id', '==', user_id)
        docs = doc_ref.get()
        for doc in docs:
            data = doc.to_dict()
            bot_token = data['bot_token']
            app_id = data['app_id']
            bot_id = data['bot_id']
            enterprise_id = data.get('enterprise_id')
            enterprise_name = data.get('enterprise_name')
            bot_installed_at = data.get('installed_at')
            bot_refresh_token = data.get('bot_refresh_token')
            return Installation(
                bot_token=bot_token,
                app_id=app_id,
                bot_id=bot_id,
                enterprise_id=enterprise_id,
                enterprise_name=enterprise_name,
                installed_at=bot_installed_at,
                bot_refresh_token=bot_refresh_token,
                team_id=data['team_id'],
                user_id=data['user_id']
            )
        else:
            return None
