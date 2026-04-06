from openai import OpenAI
from json_repair import repair_json
import json

from config import settings
from models import Report, Action, AgentState
from tools import TOOLS
from exceptions import IterationLimitReached

SYSTEM_PROMPT = """
BACKGROUND: You are a News Analyst. You evaluate all perspectives based on evidence, not assumption. When given a topic you research the topic using the 'search web' tool. Keep searching the web until you feel you have sufficient data then write a report 

RULES:
- only use URLs from collected data as sources
- represent each perspective accurately based on the weight of evidence behind it 
- search with diverse angles and opposing viewpoints, not just different queries on the same angle.

TOOLS:
- "search_web", Allows you to search the web
    - {"tool": "search_web", "args": {"query": "..."}}
- "write_injury_report", Write a report based on researched data
    - {"tool": "write_report", "args": {"goal": "...", "perspectives": [{"name": "...", "summary": "..."}, ...], "conclusion": "...", "sources": [{"url": "...", "title": "..."}, ...]}}

RESPONSE: 
- respond only in JSON
- response format: {"tool": tool_name, "args": arguments} 
- only respond with your next needed tool, there can only be one next needed tool
"""

client = OpenAI(
    base_url=settings.llm_base_url,
    api_key=settings.llm_api_key
)

def run(goal: str) -> Report:
    state = AgentState(
        goal=goal,
        history=[],
        iteration=0,
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
        if action.tool == "write_report":
            return result
        elif action.tool == "search_web": 
            state.history.append(result)

    raise IterationLimitReached("Agent exceeded max iterations without writing a report")

def think(state: AgentState) -> Action:
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT}, 
        {"role": "user", "content": f"Goal: {state.goal}"}
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
