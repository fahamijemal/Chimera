from mcp.server.fastmcp import FastMCP
import feedparser
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("chimera-news")

# Default feeds to monitor
DEFAULT_FEEDS = {
    "techcrunch": "https://techcrunch.com/feed/",
    "hackernews": "https://news.ycombinator.com/rss",
    "wired": "https://www.wired.com/feed/rss"
}

@mcp.resource("news://latest")
def get_latest_news() -> str:
    """
    Fetches the latest headlines from configured tech news sources.
    Returns a formatted string of headlines.
    """
    all_news = []
    
    # In a real async scenario, we'd fetch these concurrently
    # feedparser is blocking, so we keep it simple for now
    
    for source, url in DEFAULT_FEEDS.items():
        try:
            logger.info(f"Fetching {source} from {url}...")
            feed = feedparser.parse(url)
            
            if feed.bozo:
                logger.warning(f"Error parsing feed {source}: {feed.bozo_exception}")
                continue
                
            # Get top 5 entries
            entries = feed.entries[:5]
            for entry in entries:
                all_news.append(f"- [{source.upper()}] {entry.title} ({entry.link})")
                
        except Exception as e:
            logger.error(f"Failed to fetch {source}: {e}")
            all_news.append(f"- [{source.upper()}] Error: Could not fetch feed")

    return "\n".join(all_news)

@mcp.tool()
def read_feed(url: str, limit: int = 5) -> str:
    """
    Reads a specific RSS feed URL and returns the top items.
    
    Args:
        url: The RSS feed URL.
        limit: Number of items to return.
    """
    try:
        feed = feedparser.parse(url)
        if feed.bozo:
             return f"Error parsing feed: {feed.bozo_exception}"
        
        lines = [f"Feed: {feed.feed.get('title', url)}"]
        for entry in feed.entries[:limit]:
             lines.append(f"- {entry.title}: {entry.link}")
             
        return "\n".join(lines)
    except Exception as e:
        return f"Error reading feed: {str(e)}"

if __name__ == "__main__":
    mcp.run()
