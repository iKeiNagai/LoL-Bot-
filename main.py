import asyncio
import logging

import asqlite
import twitchio

from bot import Bot, LOGGER
from database import setup_database


# Entry point: sets up logging, opens the SQLite pool, loads saved tokens,
# starts the bot, and handles graceful shutdown on Ctrl+C.
def main() -> None:

    # Configure twitchio's built-in logging at INFO level.
    twitchio.utils.setup_logging(level=logging.INFO)

    async def runner() -> None:

        # Open (and auto-create) the SQLite database file for token storage.
        async with asqlite.create_pool("tokens.db") as token_db:
            tokens, subs = await setup_database(token_db)

            # Start the bot and load all previously saved tokens into memory.
            async with Bot(token_database=token_db, subs=subs) as bot:
                for token, refresh in tokens:
                    await bot.add_token(token, refresh)

                await bot.start(load_tokens=False)

    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        LOGGER.warning("Shutting down due to KeyboardInterrupt")


if __name__ == "__main__":
    main()