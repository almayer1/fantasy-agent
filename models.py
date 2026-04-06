from pydantic import BaseModel

class Player(BaseModel):
    name: str
    position: str
    team: str | None = None
    player_id: str | None = None

class Stats(BaseModel):
    player: Player
    fantasy_ppg: float
    games_played: int
    rec: int
    pass_yd: float
    rec_yd: float
    rush_yd: float
    rec_td: int
    rush_td: int
    fg: int
    pat: int
    rolling_rec: float
    rolling_pass_yd: float
    rolling_rec_yd: float
    rolling_rush_yd: float
    rolling_rec_td: float
    rolling_rush_td: float
    rolling_fg: float
    rolling_pat: float

class Props(BaseModel):
    player: Player
    game_date: str
    receptions: int
    passing_yards: float
    recieving_yards: float
    rushing_yards: float
    tds: int
    fantasy_points: float

class InjuryReport(BaseModel):
    player: Player
    game_status: str
    practice_status: str
    injury_description: str | None = None

class Matchup(BaseModel):
    player: Player
    opponent: str
    opponent_def_ranking: float
    team_off_ranking: float
    epa: float
    over_under: float
    spread: float

class PlayerRecommendation(BaseModel):
    player: Player
    confidence_score: float
    reasoning: str
    start: bool = False

class LineupReport(BaseModel):
    players: list[PlayerRecommendation]
    date: str
    proj_points: float

class WeeklyResult(LineupReport):
    actual_points: float

# FastAPI
class RequestOptimization(BaseModel):
    players: list[Player]

class Result(BaseModel):
    url: str
    title: str
    content: str

class SearchResult(BaseModel):
    query: str
    results: list[Result]

class InjuryAgentState(BaseModel):
    player: Player
    history: list[SearchResult]
    iteration: int
    done: bool = False

class Action(BaseModel):
    tool: str
    args: dict