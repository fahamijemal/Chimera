import pytest
import os
from chimera.mcp.client import SkillExecutor

# Ensure we use an absolute path or relative path that works from pytest root
SERVER_PATH = os.path.abspath("chimera/mcp/servers/news_server.py")

@pytest.mark.asyncio
async def test_real_news_tool_execution():
    """
    Verifies that SkillExecutor can spawn the news server and call 'fetch_headlines'.
    """
    executor = SkillExecutor(server_script_path=SERVER_PATH)
    
    try:
        # 1. Initialize
        await executor.initialize()
        
        # 2. Execute Tool
        result = await executor.execute_tool("fetch_headlines", {"topic": "AI"})
        
        # 3. Verify
        assert result["status"] == "success"
        assert "New Breakthrough in AI" in str(result["result"])
        
    finally:
        await executor.cleanup()
