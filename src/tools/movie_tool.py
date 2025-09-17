import json
import os
from typing import Dict, Any, Optional, List

from langchain_core.tools import BaseTool
from langchain_core.pydantic_v1 import BaseModel, Field, PrivateAttr

from src.schemas import MovieProperties, LookupInput, MovieAttributes
from src.tools.omdb_client import OMDBClient

class MovieLookupTool(BaseTool):
    name: str = "movie_lookup"
    description: str = (
        "Useful for looking up detailed information about a movie given its title and optionally the release year. "
        "If the year is not provided, it will search for the most relevant movie matching the title."
    )

    args_schema: type = LookupInput
    return_direct: bool = True  

    # omdb_client: OMDBClient = Field(default_factory=OMDBClient)
    # _omdb_client: OMDBClient = OMDBClient(api_key=os.getenv("OMDB_API_KEY"))
    _omdb_client: OMDBClient = OMDBClient(api_key="47124eb6")

    class Config:
        arbitrary_types_allowed = True
    
    def _normalize(self, data:Dict[str, Any]) -> Dict[str, Any]:
        return MovieAttributes.from_omdb_data(data).dict()
    
    def _run(self, title:str, year:Optional[str]=None) -> str:
        try:
            print(f"Looking up movie: title={title}, year={year}")
            detail = self._omdb_client.get_by_title(title, year)
            print(f"OMDB detail: {detail}")
            if str(detail.get("Response", "")).lower() == "true":
                if detail.get("Type", "").lower() != "movie":
                    print(f"Found title is not a movie: {detail.get('Type')}")
                    return json.dumps({
                        "status": "not_movie",
                        "message": f'The title "{title}" found, but it is not a movie (type: {detail.get("Type", "?")}).'
                    })
                print(f"Movie found: {title} ({detail.get('Year', 'unknown year')})")
                return json.dumps({
                    "status": "ok",
                    "message": f'Movie "{title}" details fetched successfully.',
                    "movie": self._normalize(detail)
                })

            search = self._omdb_client.search(title)
            if str(search.get("Response", "")).lower() == "true" and search.get("Search", None):
                print(f"Multiple candidates found for title: {title}")
                candidates = [
                    {
                        "Title": c.get("Title"),
                        "Year": c.get("Year"),
                        "Type": c.get("Type"),
                        "imdbID": c.get("imdbID"),
                    }
                    for c in search.get("Search", [])
                    if c.get("Type") == "movie"
                ][:5]
                print(f"Candidates: {candidates}")

                if candidates:
                    return json.dumps({
                        "status": "ambiguous",
                        "message": f'Multiple movies found matching the title "{title}". Please specify the exact title and year if possible.',
                        "candidates": candidates
                    })
            return json.dumps({
                "status": "error",
                "message": f'No movie found matching the title "{title}".'
            })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"An error occurred while looking up the movie: {str(e)}"
            })
    
    async def _arun(self, *args, **kwargs):
        raise NotImplementedError("MovieLookupTool does not support async")

