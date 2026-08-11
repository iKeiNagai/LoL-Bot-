from twitchio.ext import commands
from rito import RiotAPIError
from database import save_puuid, get_puuid

class LeagueComponent(commands.Component):
    def __init__(self, bot):
        self.bot = bot


    "Links a Riot ID (Name#Tag) to the current Twitch channel."
    @commands.command()
    @commands.is_broadcaster()
    async def set(self, ctx: commands.Context, riot_id: str | None = None):

        target = riot_id

        # Check argument was provided in Name#Tag format
        if not target or "#" not in target:
            await ctx.reply("Usage: !set <Name#Tag>")
            return

        # Split Riot Id into game name and tagline
        game_name, tag_line = (
            part.strip() for part in target.split("#", 1)
        )

        try: 
            # Resolve Riot ID to the account's PUUID
            puuid = await self.bot.rito.get_puuid(game_name, tag_line)
        except RiotAPIError as exc:
            # Riot's API err
            await ctx.reply(str(exc))
            return

        # Save PUUID for twitch channel in db
        await save_puuid(
            self.bot.token_database, 
            ctx.broadcaster.id, 
            puuid
        )

        # Confirmation message
        await ctx.reply(f"Linked {game_name}#{tag_line} to this channel.")