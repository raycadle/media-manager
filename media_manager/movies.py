import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env into environment

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

if not TMDB_API_KEY:
    raise RuntimeError("TMDB_API_KEY not set in environment variables.")
