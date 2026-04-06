import requests

from config import settings
from models import Player, Stats

def get_player(name: str) -> Player | None:
    players = requests.get(f"{settings.sleeper_base_url}/players/nfl").json()
    for player_id, player in players.items():
        if player.get("full_name") == name:
            return Player(
                name=player["full_name"],
                position=player["position"],
                team=player.get("team"),
                player_id=player_id
            )
    return None
    
def get_player_stats(player: Player) -> Stats:
    state = requests.get(f"{settings.sleeper_base_url}/state/nfl").json()
    current_week = state["week"]
    current_season = state["season"]
    if current_week == 0:
        current_season = state["previous_season"]
        weeks_to_fetch = 18
    else:
        weeks_to_fetch = current_week

    weeks = []
    for week in range(1, weeks_to_fetch + 1):
        week_data = requests.get(f"{settings.sleeper_base_url}/stats/nfl/regular/{current_season}/{week}").json()
        weeks.append(week_data.get(player.player_id, {}))

    last_3 = weeks[-3:]
    keys = ["rec", "pass_yd", "rec_yd", "rush_yd", "rec_td", "rush_td", "fg", "pat"]
    rolling = {key: sum(week.get(key, 0) for week in last_3) / len(last_3) for key in keys}
    total = {key: sum(week.get(key, 0) for week in weeks) for key in keys}
    
    played_weeks = [w for w in weeks if w.get("pts_ppr")]
    total["games_played"] = len(played_weeks)
    total_fantasy_points = sum(w.get("pts_ppr", 0) for w in played_weeks)
    total["fantasy_ppg"] = total_fantasy_points / total["games_played"] if total["games_played"] > 0 else 0.0


    return Stats(
        player=player,
        fantasy_ppg=total["fantasy_ppg"],
        games_played=total["games_played"],
        rec=total["rec"],
        pass_yd=total["pass_yd"],
        rec_yd=total["rec_yd"],
        rush_yd=total["rush_yd"],
        rec_td=total["rec_td"],
        rush_td=total["rush_td"],
        fg=total["fg"],
        pat=total["pat"],
        rolling_rec=rolling["rec"],
        rolling_pass_yd=rolling["pass_yd"],
        rolling_rec_yd=rolling["rec_yd"],
        rolling_rush_yd=rolling["rush_yd"],
        rolling_rec_td=rolling["rec_td"],
        rolling_rush_td=rolling["rush_td"],
        rolling_fg=rolling["fg"],
        rolling_pat=rolling["pat"]
    )
    