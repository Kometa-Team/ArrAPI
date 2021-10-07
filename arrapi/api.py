import logging
from abc import ABC, abstractmethod
from arrapi import util
from json.decoder import JSONDecodeError
from requests import Session
from requests.exceptions import RequestException
from typing import List
from .exceptions import ArrException, ConnectionFailure, Invalid, NotFound, Unauthorized
from .objs import SystemStatus, QualityProfile, MetadataProfile, RootFolder, Tag, RemotePathMapping

logger = logging.getLogger(__name__)


class BaseAPI(ABC):
    """ Base class for :class:`~arrapi.sonarr.SonarrAPI`, :class:`~arrapi.radarr.RadarrAPI`,
    :class:`~arrapi.lidarr.LidarrAPI`, and :class:`~arrapi.readarr.ReadarrAPI`
    containing API calls that are identical between Sonarr, Radarr, Lidarr, and Readarr. """

    @abstractmethod
    def __init__(self, url, apikey, v1=False, session=None):
        self.url = url.rstrip("/")
        self.apikey = apikey
        self.session = Session() if session is None else session
        self.v1 = v1
        self.v3 = True
        try:
            status = self.system_status()
        except NotFound:
            self.v3 = False
            status = self.system_status()
        if status.version is None:
            raise ConnectionFailure(f"Failed to Connect to {self.url}")
        if v1 is False:
            self.v3 = int(status.version[0]) > 2
        self.apply_tags_options = ["add", "remove", "replace"]

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
            raise ArrException(f"({response.status_code} [{response.reason}]) {response_json}")
        return response_json

    def _get_tag(self, detail=False):
        """ GET /tag and GET /tag/detail """
        return self._get("tag/detail" if detail and (self.v1 or self.v3) else "tag")

    def _post_tag(self, label):
        """ POST /tag """
        return self._post("tag", json={"label": str(label).lower()})

    def _get_tag_id(self, tag_id, detail=False):
        """ GET /tag/{id} and GET /tag/detail/{id} """
        return self._get(f"tag/detail/{tag_id}" if detail and (self.v1 or self.v3) else f"tag/{tag_id}")

    def _put_tag_id(self, tag_id, label):
        """ PUT /tag/{id} """
        return self._put(f"tag/{tag_id}", json={"id": tag_id, "label": str(label).lower()})

    def _delete_tag_id(self, tag_id):
        """ DELETE /tag/{id} """
        return self._delete(f"tag/{tag_id}")

    def _validate_tags(self, tags, create=True):
        """ Checks to see if tags are valid and if create=True will create any tags not found. """
        if not isinstance(tags, list):
            tags = [tags]

        if create is True:
            all_tag_labels = []
            all_tag_ids = []
            for tag in self.all_tags():
                all_tag_labels.append(tag.label)
                all_tag_ids.append(tag.id)
            for tag in tags:
                if not isinstance(tag, (Tag, int)) and str(tag).lower() not in all_tag_labels:
                    self._post_tag(str(tag).lower())

        all_tag_labels = {}
        all_tag_ids = []
        valid_tag_ids = []
        for tag in self.all_tags():
            all_tag_labels[tag.label] = tag.id
            all_tag_ids.append(tag.id)
        for tag in tags:
            if isinstance(tag, Tag) and tag.id in all_tag_ids:
                valid_tag_ids.append(tag.id)
            elif isinstance(tag, int) and tag in all_tag_ids:
                valid_tag_ids.append(tag)
            elif str(tag).lower() in all_tag_labels:
                valid_tag_ids.append(all_tag_labels[str(tag).lower()])

        return valid_tag_ids

    def _validate_apply_tags(self, apply_tags):
        """ Validate Apply Tags options. """
        return util.validate_options("Apply Tags", apply_tags, self.apply_tags_options)

    def get_tag(self, tag_id: int, detail: bool = False) -> Tag:
        """ Get a :class:`~arrapi.objs.Tag` by its ID.

            Parameters:
                tag_id (int): ID of Tag to get.
                detail (bool): Get Tag with details.

            Returns:
                :class:`~arrapi.objs.Tag`: Tag of the ID given.

            Raises:
                :class:`~arrapi.exceptions.NotFound`: When there's no tag with that ID.
        """
        return Tag(self, self._get_tag_id(tag_id, detail=detail))

    def all_tags(self, detail: bool = False) -> List[Tag]:
        """ Gets every :class:`~arrapi.objs.Tag`.

            Parameters:
                detail (bool): Get Tags with details.

            Returns:
                List[:class:`~arrapi.objs.Tag`]: List of all Tags.
        """
        return [Tag(self, data) for data in self._get_tag(detail=detail)]

    def create_tag(self, label: str) -> Tag:
        """ Create a new :class:`~arrapi.objs.Tag`.

            Parameters:
                label (str): Label of new Tag.

            Returns:
                :class:`~arrapi.objs.Tag`: Tag just created.
        """
        return Tag(self, self._post_tag(label))

    def edit_tag(self, tag_id: int, label: str) -> Tag:
        """ Edit a :class:`~arrapi.objs.Tag` by its ID.

            Parameters:
                tag_id (int):ID of tag to edit.
                label (str): Label to change tag to.

            Returns:
                :class:`~arrapi.objs.Tag`: Tag just edited.

            Raises:
                :class:`~arrapi.exceptions.NotFound`: When there's no tag with that ID.
        """
        return Tag(self, self._put_tag_id(tag_id, label))

    def delete_tag(self, tag_id: int) -> None:
        """ Delete a :class:`~arrapi.objs.Tag` by its ID.

            Parameters:
                tag_id (int):ID of tag to delete.

            Raises:
                :class:`~arrapi.exceptions.NotFound`: When there's no tag with that ID.
        """
        self._delete_tag_id(tag_id)

    def _get_qualityProfile(self):
        """ GET /qualityProfile for v3 and GET /profile for v2 """
        return self._get("qualityProfile" if self.v1 or self.v3 else "profile")

    def _validate_quality_profile(self, quality_profile):
        """ Validate Quality Profile options. """
        options = []
        for profile in self.quality_profile():
            options.append(profile)
            if (isinstance(quality_profile, QualityProfile) and profile.id == quality_profile.id) \
                    or (isinstance(quality_profile, int) and profile.id == quality_profile) \
                    or profile.name == quality_profile:
                return profile.id
        raise Invalid(f"Invalid Quality Profile: '{quality_profile}' Options: {options}")

    def quality_profile(self) -> List[QualityProfile]:
        """ Gets every :class:`~arrapi.objs.QualityProfile`.

            Returns:
                List[:class:`~arrapi.objs.QualityProfile`]: List of all Quality Profiles
        """
        return [QualityProfile(self, data) for data in self._get_qualityProfile()]

    def _get_rootfolder(self):
        """ GET /rootfolder """
        return self._get("rootfolder")

    def _validate_root_folder(self, root_folder):
        """ Validate Root Folder options. """
        options = []
        for folder in self.root_folder():
            options.append(folder)
            if (isinstance(root_folder, RootFolder) and folder.id == root_folder.id) \
                    or (isinstance(root_folder, int) and folder.id == root_folder) \
                    or folder.path == root_folder:
                return folder.path
        raise Invalid(f"Invalid Root Folder: '{root_folder}' Options: {options}")

    def root_folder(self) -> List[RootFolder]:
        """ Gets every :class:`~arrapi.objs.RootFolder`.

            Returns:
                List[:class:`~arrapi.objs.RootFolder`]: List of all Root Folders.
        """
        return [RootFolder(self, data) for data in self._get_rootfolder()]

    def _get_remotePathMapping(self):
        """ GET /remotePathMapping """
        return self._get("remotePathMapping")

    def remote_path_mapping(self) -> List[RemotePathMapping]:
        """ Gets every :class:`~arrapi.objs.RemotePathMapping`.

            Returns:
                List[:class:`~arrapi.objs.RemotePathMapping`]: List of all Remote Path Mappings.
        """
        return [RemotePathMapping(self, data) for data in self._get_remotePathMapping()]

    def _get_system_status(self):
        """ GET /system/status """
        return self._get("system/status")

    def system_status(self) -> SystemStatus:
        """ Gets the :class:`~arrapi.objs.SystemStatus`.

            Returns:
                :class:`~arrapi.objs.SystemStatus`: System Status Information.
        """
        return SystemStatus(self)


class BaseV1API(BaseAPI):
    """ Base class for :class:`~arrapi.lidarr.LidarrAPI` and :class:`~arrapi.readarr.ReadarrAPI`
    containing API calls that are identical between Sonarr and Radarr. """

    @abstractmethod
    def __init__(self, url, apikey, session=None):
        super().__init__(url, apikey, v1=True, session=session)

    def _get_metadataProfile(self):
        """ GET /metadataProfile """
        return self._get("metadataProfile")

    def _validate_metadata_profile(self, metadata_profile):
        """ Validate Metadata Profile options. """
        options = []
        for profile in self.metadata_profile():
            options.append(profile)
            if (isinstance(metadata_profile, MetadataProfile) and profile.id == metadata_profile.id) \
                    or (isinstance(metadata_profile, int) and profile.id == metadata_profile) \
                    or profile.name == metadata_profile:
                return profile.id
        raise Invalid(f"Invalid Metadata Profile: '{metadata_profile}' Options: {options}")

    def metadata_profile(self) -> List[MetadataProfile]:
        """ Gets every :class:`~arrapi.objs.MetadataProfile`.

            Returns:
                List[:class:`~arrapi.objs.MetadataProfile`]: List of all Metadata Profiles
        """
        return [MetadataProfile(self, data) for data in self._get_metadataProfile()]
