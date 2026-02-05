from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any

# Create a FastMCP server
# In a real deployment, we would use 'chimera-news' as the name
mcp = FastMCP("chimera-news")

@mcp.resource("news://trending")
def get_trending_news() -> str:
    """
    Returns a list of trending news topics.
    In a real app, this would fetch from NewsAPI or Bing.
    """
    # Real MCP resource returning data
    return "AI Agents, Crypto Regulation, Space Exploration"

@mcp.tool()
def fetch_headlines(topic: str) -> List[Dict[str, Any]]:
    """
    Fetches specific headlines for a topic.
    
    Args:
        topic: The topic to search for.
    """
    # Simulation of a real API call
    return [
        {
            "title": f"New Breakthrough in {topic}",
            "source": "TechDaily",
            "url": "https://example.com/1"
        },
        {
            "title": f"Why {topic} Matters in 2026",
            "source": "FutureWeb",
            "url": "https://example.com/2"
        }
    ]

if __name__ == "__main__":
    # fastmcp run will use this entry point
    mcp.run()
