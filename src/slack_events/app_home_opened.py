from config import get_env_vars
from app_instances import slack_app

settings = get_env_vars()

@slack_app.event('app_home_opened')
async def update_home_tab(client, event, logger):
    user_id = event['user']
    await client.views_publish(
        user_id=user_id,
        view={
            "type": "home",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "Musical Chair",
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Hello <@{user_id}>\n\nWelcome to the home page for the sometimes not-so-friendly music bot :musical_note::chair:"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Opt-Out",
                                "emoji": True
                            },
                            "value": "click_me_123",
                            "url": f"{settings.URL}/opt-out"
                        }
                    ]
                }
            ]
        }
    )