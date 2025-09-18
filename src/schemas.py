from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field

class MovieProperties(BaseModel):
    is_movie_query: bool = Field(..., description="Indicates if the query is about a movie.")
    title: Optional[str] = Field(None, description="The title of the movie if identified.")
    year: Optional[str] = Field(None, description="The release year of the movie if identified.")
    reasoning: Optional[str] = Field(None, description="Reasoning behind the identification of the movie title and year.")

class LookupInput(BaseModel):
    title: str = Field(..., description="The title of the movie to look up.")
    year: Optional[str] = Field(None, description="The release year of the movie to look up.")

class MovieAttributes(BaseModel):
    Title: str = Field(..., description="The title of the movie.")
    Year: str = Field(..., description="The release year of the movie.")
    Rated: Optional[str] = Field(None, description="The movie's rating.")
    Released: Optional[str] = Field(None, description="The release date of the movie.")
    Runtime: Optional[str] = Field(None, description="The runtime of the movie.")
    Genre: Optional[str] = Field(None, description="The genre(s) of the movie.")
    Director: Optional[str] = Field(None, description="The director of the movie.")
    Writer: Optional[str] = Field(None, description="The writer(s) of the movie.")
    Actors: Optional[str] = Field(None, description="The main actors in the movie.")
    Plot: Optional[str] = Field(None, description="A brief plot summary of the movie.")
    Language: Optional[str] = Field(None, description="The language(s) of the movie.")
    Awards: Optional[str] = Field(None, description="Awards won by the movie.")
    ImdbRating: Optional[str] = Field(None, description="The IMDb rating of the movie.")
    Poster: Optional[str] = Field(None, description="URL to the movie's poster image.")


    @classmethod
    def from_omdb_data(cls, data: Dict[str, Any]) -> "MovieAttributes":
        def clean(v):
            if v is None:
                return None
            s = str(v).strip()
            return None if s.upper() in ("N/A", "") else s
        
        return cls(
            Title=clean(data.get("Title")),
            Year=clean(data.get("Year")),
            Rated=clean(data.get("Rated")),
            Released=clean(data.get("Released")),
            Runtime=clean(data.get("Runtime")),
            Genre=clean(data.get("Genre")),
            Director=clean(data.get("Director")),
            Writer=clean(data.get("Writer")),
            Actors=clean(data.get("Actors")),
            Plot=clean(data.get("Plot")),
            Language=clean(data.get("Language")),
            Awards=clean(data.get("Awards")),
            ImdbRating=clean(data.get("imdbRating")),
            Poster=clean(data.get("Poster"))
        )
    
    def to_bullets(self) -> str:
        op_list = [
            ("Title", self.Title),
            ("Year", self.Year),
            ("Rated", self.Rated),
            ("Released", self.Released),
            ("Runtime", self.Runtime),
            ("Genre", self.Genre),
            ("Director", self.Director),
            ("Writer", self.Writer),
            ("Actors", self.Actors),
            ("Plot", self.Plot),
            ("Language", self.Language),
            ("Awards", self.Awards),
            ("IMDb Rating", self.ImdbRating)
        ]

        lines = [f"- **{k}**: {v}" for k, v in op_list if v]
        return "Sure! Here are the results:\n" + "\n".join(lines)
    
