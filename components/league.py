from twitchio.ext import commands
from rito import RiotAPIError
from database import save_puuid, get_puuid
from formatters import *
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


    "Fetches and displays the Solo/Duo rank for a linked account"
    @commands.command()
    async def rank(self, ctx: commands.Context):
        puuid = await get_puuid(
                    self.bot.token_database, 
                    ctx.broadcaster.id
        )

        # Check PUUID exists
        if puuid is None:
            await ctx.reply("No Riot account linked yet - use !set <Name#Tag> first.")
            return

        try:
            # Fetch raw league entries from Riot API 
            rank_rito = await self.bot.rito.get_rank_entries(puuid)
        except RiotAPIError as exc:
            # Riot's API err
            await ctx.reply(str(exc))
            return

        # Formatted ranked {tier Rank LP}
        await ctx.reply(format_rank(rank_rito))

    "Retrieves the Solo/Duo winrate for linked account"
    @commands.command()
    async def winrate(self, ctx:commands.Context):
        puuid = await get_puuid(
                    self.bot.token_database, 
                    ctx.broadcaster.id
        )

        # Check PUUID exists
        if puuid is None:
            await ctx.reply("No Riot account linked yet - use !set <Name#Tag> first.")
            return

        try:
            # Fetch raw league entries from Riot API
            rank_rito = await self.bot.rito.get_rank_entries(puuid)
        except RiotAPIError as exc:
            await ctx.reply(str(exc))
            return

        # Formatted winrate
        await ctx.reply(format_winrate(rank_rito))


    "Retrieves the summoner level for linked account"
    @commands.command()
    async def lvl(self, ctx:commands.Context):
        puuid = await get_puuid(
                    self.bot.token_database, 
                    ctx.broadcaster.id
        )
        
        # Check PUUID exists
        if puuid is None:
            await ctx.reply("No Riot account linked yet - use !set <Name#Tag> first.")
            return

        try:
            summoner = await self.bot.rito.get_player_profile(puuid)
        except RiotAPIError as exc:
            await ctx.reply(str(exc))
            return

        #
        await ctx.reply(format_level(summoner))

    "Retrieves top 3 mastery champs for linked account"
    @commands.command()
    async def mains(self, ctx:commands.Context):
        puuid = await get_puuid(
            self.bot.token_database, 
            ctx.broadcaster.id
        )
        
        # Check PUUID exists
        if puuid is None:
            await ctx.reply("No Riot account linked yet - use !set <Name#Tag> first.")
            return

        try:
            mains = await self.bot.rito.get_player_topchamps(puuid)
            champs_ids = await self.bot.static.get_champions_id()
        except RiotAPIError as exc:
            await ctx.reply(str(exc))
            return

        await ctx.reply(format_mains(mains, champs_ids))

    "Retrieves and calculates last game's pings for a linked account"
    @commands.command()
    async def pings(self, ctx: commands.Context):
        puuid = await get_puuid(
            self.bot.token_database, 
            ctx.broadcaster.id
        )
        
        # Check PUUID exists
        if puuid is None:
            await ctx.reply("No Riot account linked yet - use !set <Name#Tag> first.")
            return

        try:
            match_id = await self.bot.rito.get_match_ids(puuid)

            if not match_id:
                await ctx.reply("No recent ranked matches found.")
                return
            
            last_match_id = match_id[0]
            match_data = await self.bot.rito.get_match_info(last_match_id)
        except RiotAPIError as exc:
            await ctx.reply(str(exc))
            return

        await ctx.reply(format_last_match_pings(match_data, puuid))

        