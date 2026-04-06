from openai import OpenAI
from json_repair import repair_json
import json

from config import settings
from models import InjuryAgentState, InjuryReport, Player, Action
import tools
from exceptions import IterationLimitReached

SYSTEM_PROMPT = """
BACKGROUND: You are a Injury Researcher. Given a player you research their recent injury news, so the user knows whether to start the player or not

RULES:
- Search at least 3 times
- Verify info is accurate and recent
- Search for game status and practice status separately
- If no injury news found, report as healthy and leave injury_description blank

TOOLS:
- "search_web", Allows you to search the web.
- "write_injury_report", Write a report based on researched data.

RESPONSE FORMAT: 
- only respond with your next needed tool, there can only be one next needed tool
- respond only in JSON. see examples below
- {"tool": "write_injury_report", "args": {"player": {"name": "...", "position": "...", "team": "..."}, "game_status": "...", "practice_status": "...", "injury_description": "..."}}
- {"tool": "search_web", "args": {"query": "..."}}
"""

client = OpenAI(
    base_url=settings.llm_base_url,
    api_key=settings.llm_api_key
)

def run(player) -> InjuryReport:
    state = InjuryAgentState(
        player=player,
        history=[],
        iteration=0
    )
    # while not done and iteration are less than 10
    while not state.done and state.iteration < settings.max_iterations:
        # Think
        action = think(state)
        
        # Act
        try:
            result = TOOLS[action.tool](**action.args)
        except Exception:
            continue

        state.iteration += 1

        #Observe
        if action.tool == "write_injury_report":
            return result
        elif action.tool == "search_web": 
            state.history.append(result)

    raise IterationLimitReached("Agent exceeded max iterations without writing a report")

def think(state: InjuryAgentState) -> Action:
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT}, 
        {"role": "user", "content": f"{json.dumps(state.player.model_dump())}"}
    ]

    # History
    history = state.history
    for result in history:
        assitant = {"role": "assistant", "content": json.dumps({"tool": "search_web", "args": {"query": result.query}})}
        user = {"role": "user", "content": f"{json.dumps(result.model_dump())}"}
        messages.append(assitant)
        messages.append(user)

    # Try 3 attempts
    e = ""
    for attempt in range(3):
        # Get response
        response = client.chat.completions.create(
            model=settings.llm_model,
            messages=messages
        )
        try:
            action = json.loads(response.choices[0].message.content)
            # LLM responds with correct JSON
            return Action(**action)
        except Exception as e:
            try:
                # Try to repair
                fixed = repair_json(response.choices[0].message.content)
                return Action(**json.loads(fixed))
            except Exception:
                # Try again
                continue  

    raise ValueError(f"LLM returned invalid response: {e}")

def write_injury_report(player: Player, game_status: str, practice_status: str, injury_description: str) -> InjuryReport:
    return InjuryReport(
        player=player,
        game_status=game_status,
        practice_status=practice_status,
        injury_description=injury_description
    )

TOOLS = {
    **tools.TOOLS,
    "write_injury_report": write_injury_report
}
