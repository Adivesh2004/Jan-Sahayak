
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("ZYND_API_KEY")
if key:
    print(f"ZYND_API_KEY is found (Length: {len(key)})")
    if key == "mock_key":
        print("WARNING: Key is explicitly set to 'mock_key'")
else:
    print("ZYND_API_KEY is NOT set in environment.")
