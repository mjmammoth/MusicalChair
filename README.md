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
|Name|Necessity|Default|Description|
|-|:-:|-|-|
|`SLACK_BOT_TOKEN`|Required||Token provided on [bot creation](https://api.slack.com/apps), begins with `xoxb-`|
|`SLACK_CHANNEL_ID`|Required||Channel ID that the bot asks the question in and gets list of users from.|
|`WEEKDAYS_ONLY`|Optional|True|Set to false to post a question every day, including weekends|
|`MESSAGE_HOUR`|Optional|10|The hour that the message be posted at|
|`SCHEDULE_TIMER`|Optional|45|How often the program logic executes|
|`ONCE_A_DAY`|Optional|True|Set to false to post the question every time the program logic executes|
|`LOGGING_LEVEL`|Optional|info|Python logging level|
|`STATE_FILE`|Optional|/mnt/persistence/exclusions.json|The file where persisted state should be stored|

### ToDo
- [x] Only run on weekdays
- [x] Different prompt messages
- [x] Fetch Bot ID in runtime so that it doesn't have to be an env var
- [x] Remove already-asked users from the pool until the pool is depleted
- [x] Better config using env vars
- [ ] User opt-out
- [ ] Use time event to trigger workflow instead of having an infinite loop

### Local Dev
- Use `ngrok` to get a public URL for HTTP events.
