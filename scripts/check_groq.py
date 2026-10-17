"""Lists the Groq models available to your key.  Run: python scripts/check_groq.py"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ["GROQ_API_KEY"],
                base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"))
for m in sorted(client.models.list().data, key=lambda m: m.id):
    print(m.id)
