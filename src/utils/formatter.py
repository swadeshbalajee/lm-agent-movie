from typing import Dict, Any

def ok_payload(movie: Dict[str, Any]):
    return {
        "status": "ok",
        "message": "Movie details fetched successfully.",
        "raw": movie,
        "bullets": _bullets_from_movie(movie),
        "poster": movie.get("Poster", None)
    }

def _bullets_from_movie(movie: Dict[str, Any]) -> str:
    lines = []

    order = [
        ("Title", "Title"),
        ("Year", "Year"),
    ]