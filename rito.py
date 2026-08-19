import aiohttp


class RiotAPIError(Exception):
    """Raised for any Riot API failure that should be shown to the chatter."""

class DataDragonAPI:

    BASE_URL = "https://ddragon.leagueoflegends.com"

    def __init__(self):
        self._session : aiohttp.ClientSession | None = None
        self._version : str | None = None
        self._champions_ids : dict | None = None

    # Create and return reusable HTTP Session
    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    # Close the HTTP session
    async def close_session(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    @staticmethod
    def _raise_for_status(status: int) -> None:
        if status != 200:
            raise RiotAPIError(f"Data Dragon request failed with status {status}")

    # Gets lol latest version
    async def get_latest_version(self) -> str:
        if self._version is None:
            
            session = await self._get_session()
            url = (
                f"{self.BASE_URL}/api/versions.json"
            )

            # API request
            async with session.get(url) as response:
                self._raise_for_status(response.status)

                # Gets and sets version
                versions = await response.json()
                self._version = versions[0]

        return self._version

    # Builds and caches an {id: name} dict 
    async def get_champions_id(self) -> dict:
        if self._champions_ids is None:

            session = await self._get_session()
            version = await self.get_latest_version()

            # API endpoint
            url = (
                f"{self.BASE_URL}/cdn/{version}/data/en_US/champion.json"
            )

            # API request
            async with session.get(url) as response:
                self._raise_for_status(response.status)
                data = await response.json()

                # Saves names as id:champ in dict
                champ_data = data["data"]
                self._champions_ids = {int(v["key"]): v["name"] for v in champ_data.values()}

        return self._champions_ids


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

    # Get top 3 champion masteries info for given PUUID
    async def get_player_topchamps(self, puuid: str) -> list [dict]:
        session = await self._get_session()
        amount = 3

        # Riot API Endpoint
        url = (
            f"https://{self.server}.api.riotgames.com/lol/champion-mastery/v4/"
            f"champion-masteries/by-puuid/{puuid}/top?count={amount}"
        )

        # API request
        async with session.get(url) as response:
            self._raise_for_status(response.status)

            # Return json response
            return await response.json()

    # Get list of match ids for given PUUID
    async def get_match_ids(self, puuid: str) -> list:
        session = await self._get_session()
        type = "ranked"
        count = 20

        # Riot API Endpoint
        url = (
            f"https://{self.continent}.api.riotgames.com/lol/match/v5/"
            f"matches/by-puuid/{puuid}/ids?type={type}&start=0&count={count}"
        )

        # API request
        async with session.get(url) as response:
            self._raise_for_status(response.status)

            return await response.json()
    
    
    async def get_match_info(self, match_id: str) -> dict:
        session = await self._get_session()

        # Riot API Endpoint
        url = (
            f"https://{self.continent}.api.riotgames.com/lol/match/v5/"
            f"matches/{match_id}"
        )

        # API request
        async with session.get(url) as response:
            self._raise_for_status(response.status)

            
            return await response.json()

