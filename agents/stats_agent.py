from openai import OpenAI

from config import settings
from models import PlayerRecommendation, Stats
from api.sleeper import get_player, get_player_stats

client = OpenAI(
    api_key = settings.llm_api_key,
    base_url = settings.llm_base_url
)

def run(name: str) -> PlayerRecommendation:
    # Get Player object
    player = get_player(name)
    if player is None:
        return

    # Get Player's Stats
    stats = get_player_stats(player)

    # Generate Recommendation
    recommendation = think(stats)

def think(stats: Stats) -> PlayerRecommendation:
    pass