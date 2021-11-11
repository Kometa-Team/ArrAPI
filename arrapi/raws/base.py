import logging

from abc import ABC, abstractmethod
from json.decoder import JSONDecodeError
from requests import Session
from requests.exceptions import RequestException
from arrapi import ArrException, ConnectionFailure, NotFound, Unauthorized

logger = logging.getLogger(__name__)

class BaseRawAPI(ABC):

    @abstractmethod
    def __init__(self, url, apikey, v1=False, session=None):
        self.url = url.rstrip("/")
        self.apikey = apikey
        self.session = Session() if session is None else session
        self.v1 = v1
        self.v3 = True
        try:
            status = self.get_system_status()
        except NotFound:
            self.v3 = False
            status = self.get_system_status()
        if "version" not in status or status["version"] is None:
            raise ConnectionFailure(f"Failed to Connect to {self.url}")
        if v1 is False:
            self.v3 = int(status["version"][0]) > 2

    def _get(self, path, **kwargs):
        """ process get request. """
        return self._request("get", path, **kwargs)

    def _delete(self, path, json=None, **kwargs):
        """ process delete request. """
        return self._request("delete", path, json=json, **kwargs)

    def _post(self, path, json=None, **kwargs):
        """ process post request. """
        return self._request("post", path, json=json, **kwargs)

    def _put(self, path, json=None, **kwargs):
        """ process put request. """
        return self._request("put", path, json=json, **kwargs)

    def _request(self, request_type, path, json=None, **kwargs):
        """ process request. """
        url_params = {"apikey": f"{self.apikey}"}
        for kwarg in kwargs:
            url_params[kwarg] = kwargs[kwarg]
        request_url = f"{self.url}/api{'/v1' if self.v1 else '/v3' if self.v3 else ''}/{path}"
        if json is not None:
            logger.debug(f"Request JSON {json}")
        try:
            if request_type == "delete":
                response = self.session.delete(request_url, json=json, params=url_params)
            elif request_type == "post":
                response = self.session.post(request_url, json=json, params=url_params)
            elif request_type == "put":
                response = self.session.put(request_url, json=json, params=url_params)
            else:
                response = self.session.get(request_url, params=url_params)
            response_json = response.json()
        except (RequestException, JSONDecodeError):
            raise ConnectionFailure(f"Failed to Connect to {self.url}")
        logger.debug(f"Response ({response.status_code} [{response.reason}]) {response_json}")
        if response.status_code == 401:
            raise Unauthorized(f"({response.status_code} [{response.reason}]) Invalid API Key {response_json}")
        elif response.status_code == 404:
            raise NotFound(f"({response.status_code} [{response.reason}]) Item Not Found {response_json}")
        elif response.status_code >= 400:
            if isinstance(response_json, list) and "errorMessage" in response_json[0]:
                raise ArrException(f"({response.status_code} [{response.reason}]) {response_json[0]['errorMessage']}")
            else:
                raise ArrException(f"({response.status_code} [{response.reason}]) {response_json}")
        return response_json

    def get_tag(self, detail=False):
        """ GET /tag and GET /tag/detail """
        return self._get("tag/detail" if detail and (self.v1 or self.v3) else "tag")

    def post_tag(self, label):
        """ POST /tag """
        return self._post("tag", json={"label": str(label).lower()})

    def get_tag_id(self, tag_id, detail=False):
        """ GET /tag/{id} and GET /tag/detail/{id} """
        return self._get(f"tag/detail/{tag_id}" if detail and (self.v1 or self.v3) else f"tag/{tag_id}")

    def put_tag_id(self, tag_id, label):
        """ PUT /tag/{id} """
        return self._put(f"tag/{tag_id}", json={"id": tag_id, "label": str(label).lower()})

    def delete_tag_id(self, tag_id):
        """ DELETE /tag/{id} """
        return self._delete(f"tag/{tag_id}")

    def get_qualityProfile(self):
        """" GET /qualityProfile for v3 and GET /profile for v2 """
        return self._get("qualityProfile" if self.v1 or self.v3 else "profile")

    def get_qualityProfileId(self, qualityProfileId):
        """" GET /qualityProfile/qualityProfileId for v3 and GET /profile/qualityProfileId for v2 """
        return self._get(f"qualityProfile/{qualityProfileId}" if self.v1 or self.v3 else f"profile/{qualityProfileId}")

    def get_rootFolder(self):
        """ GET /rootFolder """
        return self._get("rootFolder")

    def post_rootFolder(self, json):
        """ POST /rootFolder """
        return self._post("rootFolder", json=json)

    def add_rootFolder(self, path):
        return self.post_rootFolder({"path": path})

    def delete_rootFolder(self, rootFolderID):
        self._delete(f"rootFolder/{rootFolderID}")

    def get_remotePathMapping(self):
        """ GET /remotePathMapping """
        return self._get("remotePathMapping")

    def get_system_status(self):
        """ GET /system/status """
        return self._get("system/status")


class BaseRawV1API(BaseRawAPI):

    @abstractmethod
    def __init__(self, url, apikey, session=None):
        super().__init__(url, apikey, v1=True, session=session)

    def get_metadataProfile(self):
        """ GET /metadataProfile """
        return self._get("metadataProfile")