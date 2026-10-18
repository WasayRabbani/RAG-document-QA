import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

GROQ_MODEL = os.getenv("GROQ_MODEL", "").strip() or "openai/gpt-oss-20b"


def create_groq_client() -> OpenAI:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")

    return OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )
