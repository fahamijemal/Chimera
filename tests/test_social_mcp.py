
import pytest
import json
from chimera.mcp.servers.social_server import post_content, get_mentions, reply_to_mention

@pytest.mark.asyncio
async def test_post_twitter_success():
    """Test posting to Twitter adapter."""
    result = await post_content("twitter", "Hello World!", [])
    assert result["platform"] == "twitter"
    assert result["status"] == "success"
    assert "tweet_" in result["id"]

@pytest.mark.asyncio
async def test_post_instagram_failure_no_media():
    """Test Instagram validation logic (needs media)."""
    result = await post_content("instagram", "No pic", [])
    assert result["status"] == "error"
    assert "media" in result["message"]

@pytest.mark.asyncio
async def test_get_mentions_resource():
    """Test fetching mentions resource."""
    # Test Twitter
    json_str = await get_mentions("twitter")
    data = json.loads(json_str)
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["platform"] == "twitter"
    assert "crypto" in data[0]["content"]

@pytest.mark.asyncio
async def test_reply_flow():
    """Test replying to a mention."""
    result = await reply_to_mention("twitter", "mention_123", "Sure thing!")
    assert result["status"] == "success"
    assert result["in_reply_to"] == "mention_123"
