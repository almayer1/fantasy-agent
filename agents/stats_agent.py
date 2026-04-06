from openai import OpenAI
from json_repair import repair_json
import json


from config import settings
from models import PlayerRecommendation, Stats
from exceptions import NoPlayer, NoResponse
from api.sleeper import get_player, get_player_stats

client = OpenAI(
    api_key = settings.llm_api_key,
    base_url = settings.llm_base_url
)
SYSTEM_PROMPT = """
    BACKGROUND: You are a fantasy football expert. Based on player stats you generate a confidence score from 1-10 on how strong of a weekly start the player is.

    INPUT: 
    - data contains NFL statistics about a certain player
    - 'rolling' refers to the average value of that stat over the last 3 games

    RULES:
    - evaluate rolling stats first, then use total stats as secondary context
    - prioritize fantasy_ppg as the best stat
    - if position is QB: prioritize rec_yd less and rush_yd more
    - if position is WR/RB/TE: prioritize rec more
    - if position is K: prioritize only fg and pat more
    - when making confidence score, don't use games played as a factor

    RESPONSE-FORMAT:
    - only responsd in JSON on a 1-10 confidence scale
    - {"player": {"name": "...", "position": "...", "team": "...", "player_id": ...}, "confidence_score": 1.0 - 10.0, "reasoning": "..."}
"""

def run(name: str) -> PlayerRecommendation:
    # Get Player object
    player = get_player(name)
    if player is None:
        raise NoPlayer("Couldn't find player. Try entering a different name")

    # Get Player's Stats
    stats = get_player_stats(player)

    # Generate Recommendation
    return think(stats)

def think(stats: Stats) -> PlayerRecommendation:
    user_prompt = json.dumps(stats.model_dump())
    for attempt in range(3):
        response = client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT}, 
                {"role": "user", "content": user_prompt}
            ]
        )
        try:
            return PlayerRecommendation(**json.loads(response.choices[0].message.content))
        except Exception:
            try:
                return PlayerRecommendation(**json.loads(repair_json(response.choices[0].message.content)))
            except Exception:
                continue
    raise NoResponse("corrupted or no LLM response")

