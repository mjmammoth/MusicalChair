from app_instances import slack_app


@slack_app.command("/musicalchair-config")
def hello_command(ack, say, command):
    ack()
    say(f"Hi there, {command['user_name']}!")
