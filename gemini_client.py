from dotenv import load_dotenv
from google import genai


def get_client():
    load_dotenv()
    return genai.Client()

        