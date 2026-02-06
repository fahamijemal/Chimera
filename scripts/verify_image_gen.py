
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chimera.mcp.servers.image_server import generate_image

def test_generation():
    load_dotenv()
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("Skipping test: GOOGLE_API_KEY not found in .env")
        return

    print("Testing image generation...")
    result = generate_image("A cute robot holding a flower", character_id="test_bot")
    
    if result.get("status") == "success":
        print(f"SUCCESS: Image generated at {result['local_path']}")
        print(f"URL: {result['url']}")
    else:
        print(f"FAILURE: {result.get('error')}")

if __name__ == "__main__":
    test_generation()
