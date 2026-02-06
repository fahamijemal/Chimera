
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def list_models():
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("No API Key found")
        return

    client = genai.Client(api_key=api_key)
    print("Listing models...")
    try:
        models = client.models.list()
        for i, m in enumerate(models):
            if i == 0:
                print(f"First model attributes: {dir(m)}")
            print(f"Model: {m.name}")
            # print(f"  DisplayName: {m.display_name}")
            # print(f"  Supported: {getattr(m, 'supported_generation_methods', 'Unknown')}")
            print("-" * 20)
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_models()
