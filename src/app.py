import os
import time
import random
from slack_bolt import App

channel_id = os.environ.get("SLACK_CHANNEL_ID")
bot_id = os.environ.get("SLACK_BOT_ID")

app = App()


def generate_message(member_id):
    questions = [
        "Hey there, <@{}>! What's your daily dose of earworms today?",
        "<@{}> Are you gonna leave us hanging or are you gonna tell us your song of the day?",
        "Alright, <@{}> - spill the tea. What's the song that's been stuck in your head all day?",
        "Okay, <@{}>. You know the drill. What's the song that's making you feel all the feels?",
        "<@{}> We need your song of the day to keep us going, don't hold out on us!",
        "Yo, <@{}>! What's the tune that's been rocking your socks today?",
        "<@{}> It's not like we need your song of the day or anything... but we kinda do, so spill the beans!",
        "Hey <@{}> - just checking in, have you found a song that's better than yesterday's yet?",
        "<@{}> Don't keep us in suspense, what's the song that's been on repeat for you today?",
        "Okay <@{}>, it's time to share. What's your song of the day? We won't judge... much.",
        "<@{}> What's your song of the day?",
        "Hey <@{}>, have you been listening to anything good today? What's your song of the day?",
        "Good morning, <@{}>! Do you have a song of the day to share with us?",
    ]
    return random.choice(questions).format(member_id)


def ask_for_song():
    members = app.client.conversations_members(channel=channel_id)
    # In some cases Apps are listed as a channel member, other cases not.
    # Remove it from the list if it exists. This solution doesn't deal with
    # other Apps and could potentially ask a bot for a song :D
    if bot_id in members["members"]:
        members["members"].remove(bot_id)
    member_id = random.choice(members["members"])
    message = generate_message(member_id)
    app.client.chat_postMessage(channel=channel_id, text=message)


def schedule_loop():
    cached_week_day = None
    while True:
        current_time = time.localtime()
        week_day = current_time.tm_wday
        if (
            current_time.tm_wday < 5         # If it's a weekday
            and current_time.tm_hour == 10   # At around 10AM
            and week_day != cached_week_day  # Run once a day only
        ):
            print('Requesting song of the day from a random group member')
            ask_for_song()
            cached_week_day = week_day

        time.sleep(45)


if __name__ == "__main__":
    print('MusicalChair bot running')
    schedule_loop()
