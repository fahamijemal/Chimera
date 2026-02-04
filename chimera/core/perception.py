from typing import List, Dict, Any
import datetime
import random

# In a real implementation, this would connect to an MCP server (e.g. news://)
# For TDD/Mocking phase, we return deterministic mock data.

def fetch_trends(topic: str) -> List[Dict[str, Any]]:
    """
    Fetches trending topics related to the query.
    
    Args:
        topic: The topic to search for (e.g., "AI Agents")
        
    Returns:
        List of dicts containing trend data complying with technical spec.
    """
    # Mock response to satisfy test_trend_fetcher.py
    mock_trends = [
        {
            "topic": topic,
            "volume": 15000,
            "sentiment_score": 0.85,
            "timestamp": datetime.datetime.now().isoformat(),
            "source": "mock_news_provider"
        },
        {
            "topic": f"{topic} Regulations",
            "volume": 5000,
            "sentiment_score": -0.2,
            "timestamp": datetime.datetime.now().isoformat(),
            "source": "mock_social_feed"
        }
    ]
    
    return mock_trends
