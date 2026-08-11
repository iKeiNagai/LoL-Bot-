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

    query2 = """CREATE TABLE IF NOT EXISTS streamer_puuids(
        user_id TEXT PRIMARY KEY REFERENCES tokens(user_id) ON DELETE CASCADE,
        puuid TEXT NOT NULL
    )"""

    async with db.acquire() as connection:
        await connection.execute(query)
        await connection.execute(query2)

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


# Insert or Update League PUUID associated with twitch user id
async def save_puuid(db: asqlite.Pool, user_id: str, puuid: str) -> None:
    query = """INSERT INTO streamer_puuids (user_id, puuid)
        VALUES (?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET puuid = excluded.puuid;
        """

    async with db.acquire() as connection:
        await connection.execute(query, (user_id, puuid))


# Retrieve League PUUID associated with twitch user id 
async def get_puuid(db: asqlite.Pool, user_id: str) -> str | None:
    query="SELECT puuid FROM streamer_puuids WHERE user_id = ?"

    async with db.acquire() as connection:
        row = await connection.fetchone(query, (user_id))

    return row["puuid"] if row else None