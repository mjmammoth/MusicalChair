# MusicalChair Slack bot :musical_note::chair:
Selects a random user in a channel and asks them for their song of the day


<img src="avatar.png" alt="MusicalChair avatar, created with MidJourney"
style="width:80%; height:80%"/>

### OAuth Scopes
|Scope|Purpose|
|-|-|
|`chat:write`|To post the message|
|`channels:read`|To get a list of all members|

### Environment Variables
|Name|Description|
|-|-|
|`SLACK_BOT_TOKEN`|Token provided on [bot creation](https://api.slack.com/apps), begins with `xoxb-`|
|`SLACK_CHANNEL_ID`|Channel ID that the bot asks the question in and gets list of users from.|

### ToDo
- [x] Only run on weekdays
- [x] Different prompt messages
- [x] Fetch Bot ID in runtime so that it doesn't have to be an env var
- [ ] Remove already-asked users from the pool until the pool is depleted
- [ ] User opt-out
- [ ] Make time-of-day for the question to be asked an env var
