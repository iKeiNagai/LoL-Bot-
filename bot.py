import logging
import asqlite
import twitchio

from twitchio import eventsub
from twitchio.ext import commands
from config import TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET, TWITCH_BOT_ID, RIOT_API_KEY
from components import *
from rito import RiotAPI

LOGGER = logging.getLogger("Bot")

# Core Bot class: handles login, token persistence, and per-broadcaster
# EventSub subscriptions for chat messages.
class Bot(commands.AutoBot):
    def __init__(self, *, token_database: asqlite.Pool, subs: list[eventsub.SubscriptionPayload]) -> None:
        # Store the DB pool so add_token() can persist tokens later.
        self.token_database = token_database

        super().__init__(
            client_id=TWITCH_CLIENT_ID,
            client_secret=TWITCH_CLIENT_SECRET,
            bot_id=TWITCH_BOT_ID,
            prefix="!",
            subscriptions=subs,     # Subscribe to all previously saved subscriptions on startup
            force_subscribe=True,   # Force re-subscribe to all subscriptions on startup to ensure they are still valid
        )

        # Initialize RiotAPI
        self.rito = RiotAPI(RIOT_API_KEY)

    # Setup hook: add all components to the bot
    async def setup_hook(self) -> None:
        await self.add_component(HelloComponent(self))
        await self.add_component(LeagueComponent(self))

    # Fired once the bot has successfully connected and authenticated
    async def event_ready(self) -> None:
        LOGGER.info("Successfully logged in as: %s", self.bot_id)

    # Fired when a new broadcaster authorizes the bot to listen to their chat messages
    async def event_oauth_authorized(self, payload: twitchio.authentication.UserTokenPayload) -> None:

        # Fires for the bot account AND every broadcaster who authorizes -> multi-user support
        await self.add_token(payload.access_token, payload.refresh_token)

        if not payload.user_id:
            return

        #
        if payload.user_id == self.bot_id:
            return

        # create eventsub subscription for the broadcaster's chat messages
        subs: list[eventsub.SubscriptionPayload] = [
            eventsub.ChatMessageSubscription(
                broadcaster_user_id=payload.user_id, 
                user_id=self.bot_id),
        ]

        # register the subscription with Twitch and log the result
        resp = await self.multi_subscribe(subs)
        if resp.errors:
            LOGGER.warning("Failed to subscribe for user %s: %r", payload.user_id, resp.errors)
        else:
            LOGGER.info("Now listening to chat for broadcaster: %s", payload.user_id)

    
    # Persist every token (bot's and each broadcaster's) to SQLite
    async def add_token(self, token: str, refresh: str) -> twitchio.authentication.ValidateTokenPayload:
        # Persist every token (bot's and each broadcaster's) to SQLite
        resp = await super().add_token(token, refresh)

        # insert a new token record or update the existing one for this user
        query = """
        INSERT INTO tokens (user_id, token, refresh)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET
            token = excluded.token,
            refresh = excluded.refresh;
        """

        async with self.token_database.acquire() as connection:
            await connection.execute(query, (resp.user_id, token, refresh))
            LOGGER.info("Saved token to database for user: %s", resp.user_id)

        return resp

    # Close riot session and bot properly
    async def close(self) -> None:
        await self.rito.close_session()
        await super().close()