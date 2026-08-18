QUEUE_TYPE = "RANKED_SOLO_5x5"

# Format rank (Tier Ranked + LP)
def format_rank(entries: list[dict]) -> str:
    # check each ranked entry
    for entry in entries:

        if entry["queueType"] == QUEUE_TYPE:
            tier = entry["tier"].capitalize()
            rank = entry["rank"]
            lp = entry["leaguePoints"]

            # Return formatted rank info 
            message = (
                f"{tier} {rank} • {lp} LP"
            )
            return message

    # Return if player isn't ranked in Solo queue
    return "unranked"

# Format Winrate (Winrate%)
def format_winrate(entries: list[dict]) -> str:
    # check each ranked entry
    for entry in entries:
        if entry["queueType"] == QUEUE_TYPE:
            wins = entry["wins"]
            losses = entry["losses"]
            total = wins + losses

            # Player's winrate
            winrate = round((wins/total) * 100, 2)

            message = (
                f"Winrate • {winrate}%"
            )
            return message

    return "unranked"

# Formats Summoner level
def format_level(entry: dict) -> str:
    summoner_level = entry["summonerLevel"]

    message = (
        f"Level • {summoner_level}"
    )

    return message