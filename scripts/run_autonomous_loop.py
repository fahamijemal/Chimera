import asyncio
import logging
from chimera.agents.planner import PlannerAgent
from dotenv import load_dotenv

# Configure logging to show info
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    load_dotenv()
    import os
    print(f"DEBUG: GOOGLE_API_KEY present: {'GOOGLE_API_KEY' in os.environ}")
    print("Initializing Planner Agent...")
    planner = PlannerAgent()
    
    print("\n--- Starting Autonomous Loop Verification ---")
    try:
        result = await planner.run_autonomous_loop()
        
        print("\n--- Loop Completed ---")
        if result["status"] == "success":
            print("✅ SUCECSS")
            print(f"News Count: {result.get('news_count')}")
            print(f"Headline: {result.get('top_headline')}")
            print(f"Generated Prompt: {result.get('generated_prompt')}")
            print(f"Image Result: {result.get('image_result')}")
        else:
            print("❌ FAILED")
            print(f"Step: {result.get('step')}")
            print(f"Error: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
