import os
import time
import random
from slack_bolt import App

# token = os.environ.get("SLACK_BOT_TOKEN"),
channel_id = os.environ.get("SLACK_CHANNEL_ID")
bot_id = os.environ.get("SLACK_BOT_ID")

app = App()


def ask_for_song():
    members = app.client.conversations_members(channel=channel_id)
    members["members"].remove(bot_id)
    member_id = random.choice(members["members"])
    message = f"Hey <@{member_id}>, what's your song of the day?"
    app.client.chat_postMessage(channel=channel_id, text=message)
    return True


def schedule_loop():
    cached_week_day = None
    while True:
        current_time = time.localtime()
        week_day = current_time.tm_wday
        if (
            current_time.tm_wday < 5         # If it's a weekday
            and current_time.tm_hour == 8   # At around 10AM
            and week_day != cached_week_day  # Run once a day only
        ):
            print('Requesting song of the day from a random group member')
            ask_for_song()
            cached_week_day = week_day

        time.sleep(45)


if __name__ == "__main__":
    print('MusicalChair bot running')
    schedule_loop()
