# MusicalChair Slack bot :musical_note::chair:
Selects a random user in a channel and asks them for their song of the day

<img src="src/avatar.png" alt="MusicalChair avatar, created with MidJourney"
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
|`SLACK_SIGNING_SECRET`|Required||Slack bot signing secret used to authenticate requests from Slack.|

### Local Dev
#### Prerequisites
* A slack workspace to which you can add a bot and edit its permissions, [create one](https://slack.com/get-started#/createnew) if needed, adding the OAuth scopes listed above.
* `Docker` - the app is containerised and the development environment uses `docker compose`
* [`ngrok`](https://ngrok.com/), used to forward an https URL to your local machine, needed to test slack [events](https://api.slack.com/events) and actions
* Set up your slack app by going to the app home under [Slack Apps](https://api.slack.com/apps)
  * Under **Features > Interactivity & Shortcuts**, enable and configure the URL to `{ngrok_url}/slack/actions`
  * Under **Features > Event Subscriptions**, enable and configure the URL to `{ngrok_url}/slack/events`
    * Subscribe to the following events: `app_home_opened`, `app_mention` and `message.channels`

Once the prerequisites are satisfied, you can begin a development environment by doing the following:
1. Use ngrok to forward traffic to your local machine, copy the URL.
```ngrok http 8000```
2. Additional to the required environment variables above, add these to your `.env` file:

|Name|Description|
|-|-|
|`DEPLOYMENT_ENV`|Set to `Local` to enable local development mocking|
|`LOCAL_URL`|Set to the https URL obtained from `ngrok`|

3. Start the docker compose application (in older docker versions, `docker-compose` needed to be downloaded separately)
```
docker compose up -d --build && docker compose logs -f
```
4. Make changes to the code to auto-restart the process inside the contianer.
