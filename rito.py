import aiohttp


class RiotAPIError(Exception):
    """Raised for any Riot API failure that should be shown to the chatter."""

 
class RiotAPI:

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.server = "na1"
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

    @staticmethod
    def _raise_for_status(status: int) -> None:
        messages = {
            400: "Riot API Bad Request",
            401: "Riot API Unauthorized",
            403: "Riot API access forbidden",
            404: "Riot API data not found",
            415: "Riot API Unsupported Media Type",
            429: "Riot API rate limit exceeded"    
        }

        if status in messages:
            raise RiotAPIError(messages[status])

        if 500 <= status < 600:
            raise RiotAPIError("Riot API server error")


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
            
            self._raise_for_status(response.status)

            # parse and return PUUID
            data = await response.json()
            return data["puuid"]


    # Get league entries for a given PUUID
    async def get_rank_entries(self, puuid: str) -> list [dict]:
        session = await self._get_session()

        # Riot API Endpoint
        url = (
            f"https://{self.server}.api.riotgames.com/lol/league/v4/"
            f"entries/by-puuid/{puuid}"
        )

        # API request
        async with session.get(url) as response:

            self._raise_for_status(response.status)
            print(await response.json())

            # Return json response
            return await response.json()

    # Get league summoner for given PUUID
    async def get_player_profile(self, puuid: str) -> dict:
        session = await self._get_session()

        # Riot API Endpoint
        url = (
            f"https://{self.server}.api.riotgames.com/lol/summoner/v4/"
            f"summoners/by-puuid/{puuid}"
        )

        # API request
        async with session.get(url) as response:
            self._raise_for_status(response.status)

            # Return json response
            return await response.json()
        
