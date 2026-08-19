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
                f"{wins}W • "
                f"{losses}L • "
                f"{winrate}%"
            )
            return message

    return "unranked"

# Formats Summoner level (Level ##)
def format_level(entry: dict) -> str:
    summoner_level = entry["summonerLevel"]

    message = (
        f"Level • {summoner_level}"
    )

    return message

# Formats user main champs (Champ [lvl ## | #### ])
def format_mains(mains: list[dict], champs_ids: dict) -> str:
    formatted_champs = []

    for champ in mains:
        champ_id = champ["championId"]
        name = champs_ids.get(champ_id, "unknown champion")

        points = champ["championPoints"]
        level= champ["championLevel"]

        # Abbreviate mastery points (1.5M, 350k, 900)
        if points >= 1_000_000:
            points_str = f"{points/1_000_000:.1f}M"
        elif points >= 1_000:
            points_str = f"{points/1_000:.0f}k"
        else:
            points_str = str(points)

        # Format individual string
        formatted_champs.append(
            f"{name} [Lvl {level} | {points_str}]"
        )

    message =(
        " • ".join(formatted_champs)
    )

    return message

# Format last match pings amount (# pings last match)
def format_last_match_pings(match_data: dict, puuid: str) -> str:

    # Selects participant from match data
    participant = next(
        p for p in match_data["info"]["participants"]
        if p["puuid"] == puuid
    )

    # Filters pings from participants data
    selected_keys = {
        key: value for key, value in participant.items()
        if key.endswith("Pings") and isinstance(value, int)
    }

    total_pings = sum(selected_keys.values())

    #print(list(selected_keys.keys()))

    message = (
        f"{total_pings} pings last game"
    )

    return message

# Formats last match details (Outcome + Champ k/d/a + ##CS + ##KDA + ##%KP)
def format_last_match(match_data: dict, puuid: str) -> str:

    # Selects participant from match data
    participant = next(
        p for p in match_data["info"]["participants"]
        if p["puuid"] == puuid
    )

    kills = participant["kills"]
    deaths = participant["deaths"]
    assist = participant["assists"]
    champion = participant["championName"]
    cs = participant["totalMinionsKilled"] + participant["neutralMinionsKilled"]
    kda = participant["challenges"]["kda"]
    kp = round(participant["challenges"]["killParticipation"] * 100,2)

    is_win = participant["win"]
    outcome = "Win" if is_win else "Loss"


    message = (
        f"{outcome} • {champion} {kills}/{deaths}/{assist} • "
        f"{cs} CS • {kda} KDA • {kp}% KP"
    )

    return message