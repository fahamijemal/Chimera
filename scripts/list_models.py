import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("Listing available models:")
for m in genai.list_models():
    print(f"- {m.name}: {m.supported_generation_methods}")
