# reddit-gafs-checker

This is a Python-based Discord bot that monitors the `reddit.com/r/GunAccessoriesForSale` subreddit for specific keywords. When a post with a matching keyword is found, the bot sends an alert to a designated Discord channel.

## Features

- **Keyword Matching**: Add keywords that the bot will monitor in the subreddit. The bot will alert when a new post contains any of the keywords.
- **Set Discord Channel**: Assign a Discord channel where the alerts will be posted.
- **Add/Remove/List Keywords**: Add, remove, or list current keywords being monitored.
- **Reddit Authentication**: Securely connect to Reddit using OAuth.

## Prerequisites

Before running this bot, ensure you have the following:

1. **Python 3.8+**
2. **Discord API Token** – You will need a Discord bot token.
3. **Reddit API Credentials** – Set up an application on Reddit to get the client ID, client secret, and other details.

### Required Python Libraries

- `asyncpraw`
- `discord.py`
- `python-dotenv`

You can install the dependencies with:

```bash
pip install -r requirements.txt
```

## Configuration

1.	Create a .env file in the project root with the following contents:
```bash
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_reddit_user_agent
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
DISCORD_BOT_TOKEN=your_discord_bot_token
```

2.	Run the Bot:

    After configuring the .env file, you can run the bot using:

```bash
python3 bot.py
```

## Commands

| Command               | Description                                     |
| --------------------- | ----------------------------------------------- |
| `!set_channel`        | Sets the current Discord channel for alerts      |
| `!add_keyword <word>` | Adds a new keyword to monitor                    |
| `!remove_keyword <word>` | Removes a keyword from the list               |
| `!list_keywords`      | Lists all currently monitored keywords           |

## Reddit Authentication

The bot uses asyncpraw for interacting with the Reddit API. Make sure you provide valid Reddit credentials in your .env file.

## Logging

This bot includes logging for better monitoring and debugging. Logs are printed in the console, showing actions such as Reddit authentication, subreddit checks, and keyword matches.

## License

This project is licensed under the MIT License.
