import pytest
import pytest_asyncio
from chimera.mcp.client import SkillExecutor

@pytest.mark.asyncio
async def test_skill_execution_contract():
    """
    Asserts that skills accept the correct parameters as defined in skills/README.md.
    """
    executor = SkillExecutor()

    # Test Case 1: Missing required 'character_id' for image gen
    # This should raise ValueError immediately (client-side validation)
    # We do NOT need to await because validation happens before connection init
    # BUT execute_tool is defined as async, so we must await or inspect the coroutine.
    # Ideally, validation is synchronous inside the async func.
    
    with pytest.raises(ValueError, match="character_id is required"):
        await executor.execute_tool("generate_image", {"prompt": "A cat"})

    # Test Case 2: Missing 'content' for tweet
    with pytest.raises(ValueError, match="content is required"):
        await executor.execute_tool("post_tweet", {})
