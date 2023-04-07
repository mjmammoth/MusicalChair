from config import settings
from app_instances import slack_app
from state_handler import state


async def get_user_home_block(user_id):
    user_in_pool = await state.is_user_in_pool(user_id)
    if user_in_pool:
        percentage_likely_to_be_asked_next = await state.get_percent_likely_to_be_asked(user_id)
        if percentage_likely_to_be_asked_next == 0:
            percent_message = ":bar_chart: You have already been asked for your song-of-the-day. You will be asked again when everyone else has been asked."
        elif percentage_likely_to_be_asked_next == 100:
            percent_message = ":bar_chart: You are guaranteed to be the next person asked for the song-of-the-day! :tada:"
        else:
            percent_message = f":bar_chart: You are {percentage_likely_to_be_asked_next}% likely to be the next person asked."
        return [
            {
                "type": "section",
                "text": {
                        "type": "mrkdwn",
                        "text": f"*Status*:\n\n:white_check_mark: You are currently *included* in the pool to be selected for your song-of-the-day.\n\n{percent_message}"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": ":x: Opt-out",
                        "emoji": True
                    },
                    "value": "click_me_123",
                    "action_id": "scheduled_question_opt_out"
                }

            }
        ]
    else:
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Status*:\n\n:x: You are currently *excluded* from song-of-the-day selections."
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": ":white_check_mark: Opt-in",
                        "emoji": True
                    },
                    "value": "click_me_123",
                    "action_id": "scheduled_question_opt_in"
                }
            }
        ]


async def home_view_template():
    return {
        "type": "home",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Welcome!",
                }
            },
            {
                "type": "image",
                "image_url": f"{settings.URL}/header",
                "alt_text": "Example image"
            },
            {
                "type": "divider"
            }
        ]
    }

footer = [
    {
        "type": "divider"
    },
    {
        "type": "context",
        "elements": [
                {
                    "type": "mrkdwn",
                    "text": "Musical Chair is an <https://github.com/mjmammoth/MusicalChair|open-source project>, contributions are welcome :leftwards_arrow_with_hook:"
                },
            {
                    "type": "plain_text",
                    "text": "Author: M J Marryatt",
                    }
        ]
    }
]


async def publish_home_view(user_id):
    home_view = await home_view_template()
    home_view['blocks'].extend(await get_user_home_block(user_id))
    home_view['blocks'].extend(footer)

    await slack_app.client.views_publish(
        user_id=user_id,
        view=home_view
    )
