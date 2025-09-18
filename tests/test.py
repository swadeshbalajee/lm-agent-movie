import os
from dotenv import load_dotenv

load_dotenv()

print(os.getenv("OMDB_API_KEY"))