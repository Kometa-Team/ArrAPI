from requests import Session
from typing import Optional
from .base import BaseRawAPI


class RadarrRawAPI(BaseRawAPI):
    def __init__(self, url: str, apikey: str, session: Optional[Session] = None) -> None:
        super().__init__(url, apikey, session=session)

    def get_movie(self, tmdb_id=None):
        """ GET /movie """
        if tmdb_id is not None:
            return self._get("movie", **{"tmdbId": tmdb_id})
        else:
            return self._get("movie")

    def get_movie_id(self, movie_id):
        """ GET /movie/{id} """
        return self._get(f"movie/{movie_id}")

    def post_movie(self, json):
        """ POST /movie """
        return self._post("movie", json=json)

    def post_movie_import(self, json):
        """ POST /movie/import """
        return self._post("movie/import", json=json)

    def put_movie(self, json, moveFiles=False):
        """ PUT /movie """
        params = {"moveFiles": "true"} if moveFiles else {}
        return self._put("movie", json=json, **params)

    def put_movie_id(self, movie_id, json, moveFiles=False):
        """ PUT /movie/{id} """
        params = {"moveFiles": "true"} if moveFiles else {}
        return self._put(f"movie/{movie_id}", json=json, **params)

    def put_movie_editor(self, json):
        """ PUT /movie/editor """
        return self._put("movie/editor", json=json)

    def delete_movie_id(self, movie_id, addImportExclusion=False, deleteFiles=False):
        """ DELETE /movie/{id} """
        params = {}
        if addImportExclusion:
            params["addImportExclusion"] = "true"
        if deleteFiles:
            params["deleteFiles"] = "true"
        self._delete(f"movie/{movie_id}", **params)

    def delete_movie_editor(self, json):
        """ DELETE /movie/editor """
        return self._delete("movie/editor", json=json)

    def get_movie_lookup(self, term):
        """ GET /movie/lookup """
        return self._get("movie/lookup", **{"term": term})

    def get_exclusions(self):
        """ GET /exclusions """
        return self._get("exclusions")

    def post_exclusions(self, json):
        """ POST /exclusions """
        return self._post("exclusions", json=json)

    def add_exclusion(self, title, tmdb_id, year):
        return self.post_exclusions({
            "movieTitle": title,
            "tmdbId": tmdb_id,
            "movieYear": year
        })
