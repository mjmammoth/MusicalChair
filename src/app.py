import os
import time
import random
import json
import logging

from slack_bolt import App

from config import settings

app = App()
logging.basicConfig(level=settings.LOGGING_LEVEL,
                    format='%(levelname)s:%(asctime)s - %(message)s')


def init_persistence():
    logging.info('Creating initial persistence file')
    bot_id = app.client.auth_test()["user_id"]
    data = {'permanent_exclusions': [bot_id],
            'already_asked': [],
            'cached_week_day': None}
    with open(settings.STATE_FILE, 'w') as f:
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
    logging.debug('Asking for the song the day from a random channel member')
    with open(settings.STATE_FILE, 'r') as f:
        data = json.load(f)
    exclusions = data['permanent_exclusions'] + data['already_asked']

    channel = app.client.conversations_members(channel=settings.CHANNEL_ID)
    channel_members = channel['members']
    remaining_pool = [uid for uid in channel_members
                      if uid not in exclusions]
    if not remaining_pool:
        logging.info('Channel member pool depleted. Refreshing pool.')
        remaining_pool = [uid for uid in channel_members
                          if uid not in data['permanent_exclusions']]
        data['already_asked'] = []

    member_id = random.choice(remaining_pool)
    message = generate_message(member_id)
    data['already_asked'].append(member_id)

    app.client.chat_postMessage(channel=settings.CHANNEL_ID, text=message)

    with open(settings.STATE_FILE, 'w') as f:
        json.dump(data, f)


def schedule_loop(dev=False):
    with open(settings.STATE_FILE, 'r') as f:
        data = json.load(f)

    cached_week_day = (data['cached_week_day']
                       if data['cached_week_day'] is not None
                       else None)

    while True:
        current_time = time.localtime()
        week_day = current_time.tm_wday

        if (
            current_time.tm_wday < settings.WEEKDAYS
            and current_time.tm_hour > settings.MESSAGE_HOUR
        ):
            if not settings.ONCE_A_DAY:
                ask_for_song()
            elif week_day != cached_week_day:
                ask_for_song()
                data['cached_week_day'] = week_day
                with open(settings.STATE_FILE, 'w') as f:
                    json.dump(data, f)

        time.sleep(settings.SCHEDULE_TIMER)


if __name__ == "__main__":
    print(u"""MusicalChair bot is running! \U0001F3B5\U0001FA91
                  .,,,.
               .;;;;;;;;;,
              ;;;'    `;;;,
             ;;;'      `;;;
             ;;;        ;;;
             ;;;.      ;;;'
             `;;;.    ;;;'
              `;;;.  ;;;'
               `;;',;;'
                ,;;;'
             ,;;;',;' ...,,,,...
          ,;;;'    ,;;;;;;;;;;;;;;,
       ,;;;'     ,;;;;;;;;;;;;;;;;;;,
      ;;;;'     ;;;',,,   `';;;;;;;;;;
     ;;;;,      ;;   ;;;     ';;;;;;;;;
    ;;;;;;       '    ;;;      ';;;;;;;
    ;;;;;;            .;;;      ;;;;;;;
    ;;;;;;,            ;;;;     ;;;;;;'
     ;;;;;;,            ;;;;   .;;;;;'
      `;;;;;;,           ;;;; ,;;;;;'
       `;;;;;;;,,,,,,,,,, ;;;; ;;;'
          `;;;;;;;;;;;;;;; ;;;; '
              ''''''''''''' ;;;.
                   .;;;.    `;;;.
                  ;;;; '     ;;;;
                  ;;;;,,,..,;;;;;
                  `;;;;;;;;;;;;;'
                    `;;;;;;;;;'
    """)

    if not os.path.isfile(settings.STATE_FILE):
        init_persistence()
    schedule_loop()
