from config import settings
from state_handler import SongOfTheDayStateHandler


async def get_user_home_block(user_id, client):
    sotd_state = SongOfTheDayStateHandler(client)
    user_in_pool = await sotd_state.is_user_in_pool(user_id)

    # User currently excluded from pool
    status_text = ':x: You are currently *excluded* from song-of-the-day selections.'
    button_text = ':white_check_mark: Opt-in'
    button_action = 'scheduled_question_opt_in'

    if user_in_pool:
        percentage_likely_to_be_asked_next = await sotd_state.get_percent_likely_to_be_asked(user_id)
        if percentage_likely_to_be_asked_next == 0:
            percent_message = ':bar_chart: You have already been asked for your song-of-the-day. You will be asked again when everyone else has been asked.'
        else:
            percent_message = f':bar_chart: You are {percentage_likely_to_be_asked_next}% likely to be the next person asked.'
        status_text = f':white_check_mark: You are currently *included* in the pool to be selected for your song-of-the-day.\n\n{percent_message}'
        button_text = ':x: Opt-out'
        button_action = 'scheduled_question_opt_out'

    return [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'*Status*:\n\n{status_text}'
            },
            'accessory': {
                'type': 'button',
                'text': {
                    'type': 'plain_text',
                    'text': button_text,
                    'emoji': True
                },
                'value': 'click_me_123',
                'action_id': button_action
            }
        }
    ]


async def home_view_template():
    return {
        'type': 'home',
        'blocks': [
            {
                'type': 'header',
                'text': {
                    'type': 'plain_text',
                    'text': 'Welcome to MusicalChair!',
                }
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': ':musical_score: Discover new music and connect over shared interests.'
                }
            },
            {
                'type': 'image',
                'image_url': f'{settings.URL}/header',
                'alt_text': 'Example image'
            },
            {
                'type': 'divider'
            }
        ]
    }

footer = [
    {
        'type': 'divider'
    },
    {
        'type': 'context',
        'elements': [
                {
                    'type': 'mrkdwn',
                    'text': 'MusicalChair is an <https://github.com/mjmammoth/MusicalChair|open-source project>, contributions are welcome :leftwards_arrow_with_hook:'
                },
        ]
    }
]


async def publish_home_view(user_id, client):
    home_view = await home_view_template()
    home_view['blocks'].extend(await get_user_home_block(user_id, client))
    home_view['blocks'].extend(footer)

    await client.views_publish(
        user_id=user_id,
        view=home_view
    )
