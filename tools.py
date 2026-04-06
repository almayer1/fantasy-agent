from tavily import TavilyClient

from config import settings
from models import SearchResult, Result

def search_web(query: str) -> SearchResult:
    # Search web
    client = TavilyClient(api_key=settings.tavily_api_key)
    response = client.search(query)
    
    # Extract results
    results = []
    for result in response["results"]:
        results.append(
            Result(
                url=result["url"],
                title=result["title"],
                content=result["content"]
            )
        )

    return SearchResult(
        query=query,
        results=results
    )
