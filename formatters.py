
def format_rank(entries: list[dict]) -> str:
    queuetype= "RANKED_SOLO_5x5"

    # check each ranked entry
    for entry in entries:

        if entry["queueType"] == queuetype:
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
