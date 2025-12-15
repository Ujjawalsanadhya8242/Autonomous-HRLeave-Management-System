# check_models.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from your .env file
load_dotenv()

# Configure the client with your key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found. Please set it in your .env file.")

genai.configure(api_key=api_key)

print("✅ Available Gemini models that support 'generateContent':")
# List all models and check which ones support the 'generateContent' method
for m in genai.list_models():
  if 'generateContent' in m.supported_generation_methods:
    print(m.name)