import sqlite3

import asqlite
from twitchio import eventsub

from config import TWITCH_BOT_ID


# Handles creation of the SQLite token store and loading any previously
# saved tokens/subscriptions back into memory on startup.
async def setup_database(db: asqlite.Pool) -> tuple[list[tuple[str, str]], list[eventsub.SubscriptionPayload]]:

    # Create the tokens table if it doesn't exist yet
    query = """CREATE TABLE IF NOT EXISTS tokens(
        user_id TEXT PRIMARY KEY,
        token TEXT NOT NULL,
        refresh TEXT NOT NULL
    )"""

    async with db.acquire() as connection:
        await connection.execute(query)

        # Fetch all previously saved tokens/subscriptions from the database
        rows: list[sqlite3.Row] = await connection.fetchall("SELECT * FROM tokens")

    tokens: list[tuple[str, str]] = []
    subs: list[eventsub.SubscriptionPayload] = []

    for row in rows:

        # Add the token/refresh pair to the list of tokens to load into memory
        tokens.append((row["token"], row["refresh"]))

        # Dont re-subscribe to bot's own chat,
        # it doesnt need a chat subscription for itself
        if row["user_id"] == TWITCH_BOT_ID:
            continue

        # Re-subscribe to every broadcaster that authorized in a previous run
        subs.append(
            eventsub.ChatMessageSubscription(
                broadcaster_user_id=row["user_id"], 
                user_id=TWITCH_BOT_ID))

    return tokens, subs