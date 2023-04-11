# MusicalChair Slack bot :musical_note::chair:
Selects a random user in a channel and asks them for their song of the day

<a href="https://slack.com/oauth/v2/authorize?scope=&amp;user_scope=&amp;redirect_uri=https%3A%2F%2Fcb6a-197-90-67-146.ngrok-free.app%2Fslack%2Foauth&amp;client_id=4846572958851.4840099285526" style="align-items:center;color:#000;background-color:#fff;border:1px solid #ddd;border-radius:4px;display:inline-flex;font-family:Lato, sans-serif;font-size:16px;font-weight:600;height:48px;justify-content:center;text-decoration:none;width:236px"><svg xmlns="http://www.w3.org/2000/svg" style="height:20px;width:20px;margin-right:12px" viewBox="0 0 122.8 122.8"><path d="M25.8 77.6c0 7.1-5.8 12.9-12.9 12.9S0 84.7 0 77.6s5.8-12.9 12.9-12.9h12.9v12.9zm6.5 0c0-7.1 5.8-12.9 12.9-12.9s12.9 5.8 12.9 12.9v32.3c0 7.1-5.8 12.9-12.9 12.9s-12.9-5.8-12.9-12.9V77.6z" fill="#e01e5a"></path><path d="M45.2 25.8c-7.1 0-12.9-5.8-12.9-12.9S38.1 0 45.2 0s12.9 5.8 12.9 12.9v12.9H45.2zm0 6.5c7.1 0 12.9 5.8 12.9 12.9s-5.8 12.9-12.9 12.9H12.9C5.8 58.1 0 52.3 0 45.2s5.8-12.9 12.9-12.9h32.3z" fill="#36c5f0"></path><path d="M97 45.2c0-7.1 5.8-12.9 12.9-12.9s12.9 5.8 12.9 12.9-5.8 12.9-12.9 12.9H97V45.2zm-6.5 0c0 7.1-5.8 12.9-12.9 12.9s-12.9-5.8-12.9-12.9V12.9C64.7 5.8 70.5 0 77.6 0s12.9 5.8 12.9 12.9v32.3z" fill="#2eb67d"></path><path d="M77.6 97c7.1 0 12.9 5.8 12.9 12.9s-5.8 12.9-12.9 12.9-12.9-5.8-12.9-12.9V97h12.9zm0-6.5c-7.1 0-12.9-5.8-12.9-12.9s5.8-12.9 12.9-12.9h32.3c7.1 0 12.9 5.8 12.9 12.9s-5.8 12.9-12.9 12.9H77.6z" fill="#ecb22e"></path></svg>Add to Slack</a>

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
*. Use ngrok to forward traffic to your local machine, copy the URL.
```ngrok http 8000```
* Set up your slack app by going to the app home under [Slack Apps](https://api.slack.com/apps)
  * Under **Features > Interactivity & Shortcuts**, enable and configure the URL to `{ngrok_url}/slack/actions`
  * Under **Features > Event Subscriptions**, enable and configure the URL to `{ngrok_url}/slack/events`
    * Subscribe to the following events: `app_home_opened`, `app_mention` and `message.channels`
* Additional to the required standard environment variables, add these to your `.env` file:

|Name|Description|
|-|-|
|`DEPLOYMENT_ENV`|Set to `Local` to enable local development mocking|
|`LOCAL_URL`|Set to the https URL obtained from `ngrok`|


#### Local dev loop
1. Start the docker compose application (in older docker versions, `docker-compose` needed to be downloaded separately)
```
docker compose up -d --build && docker compose logs -f
```
2. Make changes to the code to auto-restart the process inside the contianer.
