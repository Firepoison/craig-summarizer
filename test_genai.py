from google import genai
from google.genai import types

try:
    client = genai.Client()
    print("Client initialized")
except Exception as e:
    print(f"Error: {e}")
