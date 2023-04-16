import random

from config import settings
from storage import FIRESTORE_CLIENT

doc = FIRESTORE_CLIENT.collection(settings.COLLECTION).document('state')


class SongOfTheDayStateHandler:
    def __init__(self, slack_client):
        self.slack_client = slack_client
        self.state = None

    async def get_state(self):
        if self.state is None:
            state = doc.get()
            if not state.exists or state.to_dict()['already_asked'] is None:
                bot_id = await self.slack_client.auth_test()
                state = {'permanent_exclusions': [bot_id['user_id']],
                         'already_asked': []}
                doc.set(state)
            else:
                state = state.to_dict()
            self.state = state
        return self.state

    async def is_user_in_pool(self, user_id):
        state = await self.get_state()
        if user_id not in state['permanent_exclusions']:
            return True
        return False

    async def is_user_already_asked(self, user_id):
        state = await self.get_state()
        if user_id in state['already_asked']:
            return True
        return False

    async def add_user_to_already_asked(self, user_id):
        state = await self.get_state()
        state['already_asked'].append(user_id)
        doc.set(state)
        self.state = None

    async def add_user_to_permanent_exclusions(self, user_id):
        state = await self.get_state()
        state['permanent_exclusions'].append(user_id)
        doc.set(state)
        self.state = None

    async def remove_user_from_permanent_exclusions(self, user_id):
        state = await self.get_state()
        state['permanent_exclusions'].remove(user_id)
        doc.set(state)
        self.state = None

    async def get_permanent_exclusions(self):
        state = await self.get_state()
        return state['permanent_exclusions']

    async def get_all_exclusions(self):
        state = await self.get_state()
        return state['permanent_exclusions'] + state['already_asked']

    async def get_remaining_pool(self):
        state = await self.get_state()
        exclusions = await self.get_all_exclusions()
        channel = await self.slack_client.conversations_members(
            channel=settings.CHANNEL_ID
        )
        channel_members = channel['members']
        remaining_pool = [uid for uid in channel_members
                          if uid not in exclusions]

        if not remaining_pool:
            remaining_pool = [uid for uid in channel_members
                              if uid not in state['permanent_exclusions']]
            state['already_asked'] = []
        return remaining_pool

    async def get_random_member_from_pool(self):
        remaining_pool = await self.get_remaining_pool()
        return random.choice(remaining_pool)

    async def get_percent_likely_to_be_asked(self, user_id):
        if await self.is_user_already_asked(user_id):
            return 0

        remaining_pool = await self.get_remaining_pool()
        remaining_pool_size = len(remaining_pool)
        return round((1 / remaining_pool_size) * 100)
