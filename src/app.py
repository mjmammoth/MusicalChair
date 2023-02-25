import os
import time
import random
import json

from slack_bolt import App

from config import settings

app = App()


def init_persistence():
    print('Creating initial persistence file')
    bot_id = app.client.auth_test()["user_id"]
    print(bot_id)
    data = {'permanent_exclusions': [bot_id], 'already_asked': []}
    with open(PERSISTENCE_FILE, 'w') as f:
        json.dump(data, f)


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
    with open(PERSISTENCE_FILE, 'r') as f:
        data = json.load(f)
    exclusions = data['permanent_exclusions'] + data['already_asked']

    channel_info = app.client.conversations_members(channel=CHANNEL_ID)
    channel_members = channel_info['members']
    remaining_pool = [uid for uid in channel_members
                      if uid not in exclusions]
    if not remaining_pool:
        remaining_pool = [uid for uid in channel_members
                          if uid not in data['permanent_exclusions']]
        data['already_asked'] = []

    member_id = random.choice(remaining_pool)
    message = generate_message(member_id)
    data['already_asked'].append(member_id)

    app.client.chat_postMessage(channel=CHANNEL_ID, text=message)

    with open(PERSISTENCE_FILE, 'w') as f:
        json.dump(data, f)


def schedule_loop(dev=False):
    if not dev:
        wday = 5
        hour = 10
    else:
        wday = 7
    cached_week_day = None
    while True:
        current_time = time.localtime()
        week_day = current_time.tm_wday
        if should_send_message():
            print('Requesting song of the day from a random group member')
            ask_for_song()
            cached_week_day = week_day

        if (
            current_time.tm_wday < settings.         # If it's a weekday
            and current_time.tm_hour > settings.MESSAGE_HOUR   # At around 10AM
            and week_day != cached_week_day  # Run once a day only
        ):

        time.sleep(settings.SCHEDULE_TIMER)


if __name__ == "__main__":
    print('MusicalChair bot running')
    if not os.path.isfile(PERSISTENCE_FILE):
        init_persistence()
    schedule_loop()
