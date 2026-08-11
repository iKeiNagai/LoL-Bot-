import aiohttp


class RiotAPIError(Exception):
    """Raised for any Riot API failure that should be shown to the chatter."""

 
class RiotAPI:

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.platform = "na1"
        self.continent = "americas"
        self._session : aiohttp.ClientSession | None = None 


    # Create and return reusable HTTP Session
    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={
                    "X-Riot-Token": self.api_key
            })
        return self._session

    # Close the HTTP session
    async def close_session(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()


    # Look up Riot ID and return account's PUUID
    async def get_puuid(self, game_name: str, tag_line: str) -> str:
        session = await self._get_session()

        # Riot API Endpoint
        url = (
            f"https://{self.continent}.api.riotgames.com/riot/account/v1/"
            f"accounts/by-riot-id/{game_name}/{tag_line}"
        )

        # API request
        async with session.get(url) as response:
            if response.status == 404:
                raise RiotAPIError(
                    f"Player '{game_name}#{tag_line}' not found."
                )

            # parse and return PUUID
            data = await response.json()
            return data["puuid"]