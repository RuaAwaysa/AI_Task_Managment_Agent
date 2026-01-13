"""
Serper Web Search Tool
This module provides a simple search interface for AI agents
"""
from typing import List, Dict
from observability.langfuse_config import log_agent_event

def serper_search(query: str, max_results: int = 5) -> List[Dict]:
    """
    Perform a web search using Serper (simulated)
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
    
    Returns:
        List of search results as dictionaries with 'title' and 'link'
    """
    log_agent_event(
        event_name="serper_search_called",
        agent_name="serper_tool",
        data={"query": query, "max_results": max_results}
    )

    # Simulated results
    results = [
        {"title": f"Result {i+1} for '{query}'", "link": f"https://example.com/{i+1}"}
        for i in range(max_results)
    ]
    
    log_agent_event(
        event_name="serper_search_results",
        agent_name="serper_tool",
        data={"query": query, "results_count": len(results)}
    )
    
    return results