import asyncio
import asyncpraw
import discord
from discord.ext import tasks, commands
import asyncprawcore
import logging
import os
from config import Config
from dotenv import load_dotenv


# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Global variables
SUBREDDIT_NAME = 'GunAccessoriesForSale'
DISCORD_CHANNEL_ID = None  # Will be set by the set_channel command
KEYWORDS = set()  # Will be populated by the add_keyword command
reddit = None  # Global Reddit instance

load_dotenv()

# Load Reddit API credentials from environment variables
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')
REDDIT_USERNAME = os.getenv('REDDIT_USERNAME')
REDDIT_PASSWORD = os.getenv('REDDIT_PASSWORD')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

@bot.event
async def on_ready():
    global reddit
    print(f'Logged in as {bot.user}')
    logging.info(f'Bot logged in as {bot.user}')
    reddit = await authenticate_reddit()  # Authenticate once when the bot starts
    if reddit:
        logging.info('Reddit authenticated successfully.')
    else:
        logging.error('Failed to authenticate with Reddit.')
    check_reddit_loop.start()

@bot.command()
async def set_channel(ctx):
    global DISCORD_CHANNEL_ID
    DISCORD_CHANNEL_ID = ctx.channel.id
    await ctx.send(f"Channel set to {ctx.channel.name}")
    logging.info(f"Channel set to {ctx.channel.name} (ID: {DISCORD_CHANNEL_ID})")

@bot.command()
async def add_keyword(ctx, keyword: str):
    KEYWORDS.add(keyword.lower())
    await ctx.send(f"Added keyword: {keyword}")
    logging.info(f"Added keyword: {keyword}")
    await ctx.send(f"Current keywords: {', '.join(KEYWORDS)}")

@bot.command()
async def remove_keyword(ctx, keyword: str):
    if keyword.lower() in KEYWORDS:
        KEYWORDS.remove(keyword.lower())
        await ctx.send(f"Removed keyword: {keyword}")
        logging.info(f"Removed keyword: {keyword}")
    else:
        await ctx.send(f"Keyword not found: {keyword}")
    await ctx.send(f"Current keywords: {', '.join(KEYWORDS)}")

@bot.command()
async def list_keywords(ctx):
    if KEYWORDS:
        await ctx.send("Current keywords: " + ", ".join(KEYWORDS))
    else:
        await ctx.send("No keywords set")
    logging.info(f"Listed keywords: {', '.join(KEYWORDS)}")


async def authenticate_reddit():
    try:
        logging.debug(f"Attempting to authenticate with Reddit using client_id: {REDDIT_CLIENT_ID[:5]}...")
        session = asyncpraw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT,
            username=REDDIT_USERNAME,
            password=REDDIT_PASSWORD
        )
        logging.debug("Reddit instance created. Attempting to get user information...")
        me = await session.user.me()
        if me is None:
            logging.error("Reddit.user.me() returned None. Authentication failed.")
            return None

        logging.debug(f"Authenticated as Reddit user: {me.name}")
        return session
    except asyncprawcore.exceptions.OAuthException as oauth_error:
        logging.error(f"Reddit OAuth error: {oauth_error}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during Reddit authentication: {e}", exc_info=True)
        return None

        logging.debug("Reddit instance created. Attempting to get user information...")
        me = await session.user.me()
        if me is None:
            logging.error("Reddit.user.me() returned None. Authentication failed.")
            return None

        logging.debug(f"Authenticated as Reddit user: {me.name}")
        return session
    except asyncprawcore.exceptions.OAuthException as oauth_error:
        logging.error(f"Reddit OAuth error: {oauth_error}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during Reddit authentication: {e}", exc_info=True)
        return None

@tasks.loop(minutes=1)
async def check_reddit_loop():
    logging.debug("Starting Reddit check")
    if not DISCORD_CHANNEL_ID or not KEYWORDS:
        logging.warning("Discord channel not set or no keywords defined")
        return

    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    if not channel:
        logging.error("Discord channel not found")
        return

    if not reddit:
        logging.error("Reddit instance not available. Skipping this check.")
        return

    try:
        subreddit = await reddit.subreddit(SUBREDDIT_NAME)
        logging.debug(f"Checking subreddit: {SUBREDDIT_NAME}")
        async for submission in subreddit.new(limit=2):  # Check the latest 2 posts
            logging.debug(f"Examining post: {submission.title}")
            if any(keyword.lower() in submission.title.lower() for keyword in KEYWORDS):
                logging.info(f"Keyword match found: {submission.title}")
                await channel.send(f"Keyword match found:\nTitle: {submission.title}\nURL: {submission.url}")
            else:
                logging.debug(f"No keyword match for: {submission.title}")
    except asyncprawcore.exceptions.ResponseException as response_error:
        logging.error(f"Reddit API response error: {response_error}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)

    logging.debug("Finished Reddit check")

@check_reddit_loop.before_loop
async def before_check_reddit_loop():
    await bot.wait_until_ready()

# Ensure the Reddit session is closed when the bot shuts down
@bot.event
async def on_close():
    if reddit:
        await reddit.close()
        logging.debug("Reddit session closed.")

# Run the bot (Make sure to replace with a secure way of loading your token)
bot.run(DISCORD_BOT_TOKEN)
