from app_instances import slack_app
from state_handler import SongOfTheDayStateHandler
from functions import publish_home_view


@slack_app.action('scheduled_question_opt_in')
async def opt_in(ack, body, client, logger):
    sotd_state = SongOfTheDayStateHandler(slack_app.client)
    await sotd_state.remove_user_from_permanent_exclusions(body['user']['id'])
    await publish_home_view(body['user']['id'], client)
    await ack()


@slack_app.action('scheduled_question_opt_out')
async def opt_outhandle_action(ack, body, client, logger):
    sotd_state = SongOfTheDayStateHandler(slack_app.client)
    await sotd_state.add_user_to_permanent_exclusions(body['user']['id'])
    await publish_home_view(body['user']['id'], client)
    await ack()
