from storage import FIRESTORE_CLIENT as db


def get_bot_token_for_team(team_id):
    """Get the bot token for a team"""
    return db.collection('installations').document(team_id).get().to_dict()['bot_token']
