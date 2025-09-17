import os

def validate_env():
    openai_key = os.getenv("OPENAI_API_KEY")
    omdb_key = os.getenv("OMDB_API_KEY")

    if not openai_key and omdb_key:
        return False, "Missing OPENAI_API_KEY in environment variables."
    if not openai_key:
        return False, "Missing OPENAI_API_KEY in environment variables."
    if not omdb_key:
        return False, "Missing OMDB_API_KEY in environment variables."  
    
    return True, None

def get_model():
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")