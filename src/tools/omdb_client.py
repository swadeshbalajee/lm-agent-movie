import os
import time
import re
import requests
from typing import Optional, List, Dict, Any

OMBD_API_URL = "http://www.omdbapi.com/"

class OMDBClient:
    def __init__(self, api_key:Optional[str]=None, timeout:int=10, retires:int=2):
        self.api_key = api_key or os.getenv("OMDB_API_KEY")
        if not self.api_key:
            raise ValueError("OMDB API key is required. Please set the OMDB_API_KEY environment variable.")
        
        self.timeout = timeout
        self.retries = retires
    
    def _request(self, params:Dict[str, Any]) -> Dict[str, Any]:
        params = {**params, "apikey": self.api_key}
        last_err = None

        for attempt in range(self.retries):
            try:
                response = requests.get(OMBD_API_URL, params=params, timeout=self.timeout)
                if response.status_code == 401:
                    raise ValueError("Unauthorized: Invalid OMDB API key.")
                if response.status_code == 403:
                    raise ValueError("Forbidden: You do not have access to the OMDB API.")

                response.raise_for_status()

                return response.json()
            except Exception as e:
                last_err = e
                if attempt < self.retries:
                    time.sleep(0.4 ** (attempt + 1))
                else:
                    raise
        
        raise last_err or RuntimeError("Failed to make request to OMDB API.")
    
    def get_by_title(self, title:str, year:Optional[str]=None) -> Dict[str, Any]:
        params = {
            "t": title,
            "plot": "plot",
            "type": "movie"
        }
        if year and re.fullmatch(r"\d{4}", year):
            params["y"] = year
        
        return self._request(params)

    def search(self, title:str) -> List[Dict[str, Any]]:
        params = {
            "s": title,
            "type": "movie"
        }
        data = self._request(params)
        return data
        