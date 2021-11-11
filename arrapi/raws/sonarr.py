from requests import Session
from typing import Optional
from .base import BaseRawAPI

class SonarrRawAPI(BaseRawAPI):
    def __init__(self, url: str, apikey: str, session: Optional[Session] = None) -> None:
        super().__init__(url, apikey, session=session)

    def get_series(self, tvdb_id=None):
        """ GET /series """
        if tvdb_id is not None:
            return self._get("series", **{"tvdbId": tvdb_id})
        else:
            return self._get("series")

    def get_series_id(self, series_id):
        """ GET /series/{id} """
        return self._get(f"series/{series_id}")

    def post_series(self, json):
        """ POST /series """
        return self._post("series", json=json)

    def post_series_import(self, json):
        """ POST /series/import """
        return self._post("series/import", json=json)

    def put_series(self, json, moveFiles=False):
        """ PUT /series """
        params = {"moveFiles": "true"} if moveFiles else {}
        return self._put("series", json=json, **params)

    def put_series_id(self, series_id, json, moveFiles=False):
        """ PUT /series/{id} """
        params = {"moveFiles": "true"} if moveFiles else {}
        return self._put(f"series/{series_id}", json=json, **params)

    def put_series_editor(self, json):
        """ PUT /series/editor """
        return self._put("series/editor", json=json)

    def delete_series_id(self, series_id, addImportExclusion=False, deleteFiles=False):
        """ DELETE /series/{id} """
        params = {}
        if addImportExclusion:
            params["addImportExclusion"] = "true"
        if deleteFiles:
            params["deleteFiles"] = "true"
        self._delete(f"series/{series_id}", **params)

    def delete_series_editor(self, json):
        """ DELETE /series/editor """
        return self._delete("series/editor", json=json)

    def get_series_lookup(self, term):
        """ GET /series/lookup """
        return self._get("series/lookup", **{"term": term})

    def post_seasonPass(self, json):
        """ POST /seasonPass """
        return self._post("seasonPass", json=json)

    def edit_series_monitoring(self, series_ids, monitor):
        """ Edit multiple Series monitoring """
        if not isinstance(series_ids, list):
            series_ids = [series_ids]
        monitored = monitor != "none"
        json = {
            "monitoringOptions": {"monitor": monitor},
            "series": [{"id": s, "monitored": monitored} for s in series_ids]
        }
        return self.post_seasonPass(json)

    def get_languageProfile(self):
        """ GET /languageProfile """
        return self._get("languageProfile")

    def get_languageProfileId(self, languageProfileId):
        """" GET /languageProfile/languageProfileId """
        return self._get(f"languageProfile/{languageProfileId}")

    def get_importlistexclusion(self):
        """ GET /importlistexclusion """
        return self._get("importlistexclusion")

    def post_importlistexclusion(self, json):
        """ POST /importlistexclusion """
        return self._post("importlistexclusion", json=json)

    def add_importlistexclusion(self, title, tvdb_id):
        return self.post_importlistexclusion({
            "title": title,
            "tvdbId": tvdb_id
        })