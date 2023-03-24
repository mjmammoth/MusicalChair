from app_instances import slack_app


@slack_app.event('app_mention')
async def handle_mention(event, say):
    await say('I received your message!')
