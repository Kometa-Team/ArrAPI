from abc import ABC, abstractmethod
from arrapi import Invalid, SystemStatus, QualityProfile, MetadataProfile, RootFolder, Tag, RemotePathMapping
from typing import List


class BaseAPI(ABC):
    @abstractmethod
    def __init__(self, raw):
        self._raw = raw
        self.apply_tags_options = ["add", "remove", "replace"]

    def _validate_options(self, title: str, value: str, options: List[str]):
        """ Validate the value given from the options given.

            Parameters:
                title (str): Name of what is being validated.
                value (str): Value to check options for.
                options (List[str]): List of options to check the value against.

            Returns:
                str: Valid Value

            Raises:
                :class:`~arrapi.exceptions.Invalid`: If the value isn't in the options.
        """
        if value in options:
            return value
        raise Invalid(f"Invalid {title}: '{value}' Options: {options}")

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
                    self._raw.post_tag(str(tag).lower())

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
        return self._validate_options("Apply Tags", apply_tags, self.apply_tags_options)

    def get_tag(self, tag_id: int, detail: bool = False) -> Tag:
        """ Get a :class:`~arrapi.objs.reload.Tag` by its ID.

            Parameters:
                tag_id (int): ID of Tag to get.
                detail (bool): Get Tag with details.

            Returns:
                :class:`~arrapi.objs.reload.Tag`: Tag of the ID given.

            Raises:
                :class:`~arrapi.exceptions.NotFound`: When there's no tag with that ID.
        """
        return Tag(self, self._raw.get_tag_id(tag_id, detail=detail))

    def all_tags(self, detail: bool = False) -> List[Tag]:
        """ Gets every :class:`~arrapi.objs.reload.Tag`.

            Parameters:
                detail (bool): Get Tags with details.

            Returns:
                List[:class:`~arrapi.objs.reload.Tag`]: List of all Tags.
        """
        return [Tag(self, data) for data in self._raw.get_tag(detail=detail)]

    def create_tag(self, label: str) -> Tag:
        """ Create a new :class:`~arrapi.objs.reload.Tag`.

            Parameters:
                label (str): Label of new Tag.

            Returns:
                :class:`~arrapi.objs.reload.Tag`: Tag just created.
        """
        return Tag(self, self._raw.post_tag(label))

    def edit_tag(self, tag_id: int, label: str) -> Tag:
        """ Edit a :class:`~arrapi.objs.reload.Tag` by its ID.

            Parameters:
                tag_id (int): ID of tag to edit.
                label (str): Label to change tag to.

            Returns:
                :class:`~arrapi.objs.reload.Tag`: Tag just edited.

            Raises:
                :class:`~arrapi.exceptions.NotFound`: When there's no tag with that ID.
        """
        return Tag(self, self._raw.put_tag_id(tag_id, label))

    def delete_tag(self, tag_id: int) -> None:
        """ Delete a :class:`~arrapi.objs.reload.Tag` by its ID.

            Parameters:
                tag_id (int): ID of tag to delete.

            Raises:
                :class:`~arrapi.exceptions.NotFound`: When there's no tag with that ID.
        """
        self._raw.delete_tag_id(tag_id)

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
        """ Gets every :class:`~arrapi.objs.simple.QualityProfile`.

            Returns:
                List[:class:`~arrapi.objs.simple.QualityProfile`]: List of all Quality Profiles
        """
        return [QualityProfile(self, data) for data in self._raw.get_qualityProfile()]

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
        """ Gets every :class:`~arrapi.objs.simple.RootFolder`.

            Returns:
                List[:class:`~arrapi.objs.simple.RootFolder`]: List of all Root Folders.
        """
        return [RootFolder(self, data) for data in self._raw.get_rootFolder()]

    def add_root_folder(self, path):
        """ Adds the path given as a root folder

            Parameters:
                path (str): path of new root folder

            Raises:
                :class:`~arrapi.exceptions.ArrException`: When the path does not exist or is already a root folder
        """
        self._raw.add_rootFolder(path)

    def remote_path_mapping(self) -> List[RemotePathMapping]:
        """ Gets every :class:`~arrapi.objs.simple.RemotePathMapping`.

            Returns:
                List[:class:`~arrapi.objs.simple.RemotePathMapping`]: List of all Remote Path Mappings.
        """
        return [RemotePathMapping(self, data) for data in self._raw.get_remotePathMapping()]

    def system_status(self) -> SystemStatus:
        """ Gets the :class:`~arrapi.objs.relaod.SystemStatus`.

            Returns:
                :class:`~arrapi.objs.reload.SystemStatus`: System Status Information.
        """
        return SystemStatus(self)


class BaseV1API(BaseAPI):
    """ Base class for :class:`~arrapi.apis.lidarr.LidarrAPI` and :class:`~arrapi.apis.readarr.ReadarrAPI`
    containing API calls that are identical between Sonarr and Radarr. """

    @abstractmethod
    def __init__(self, raw):
        super().__init__(raw)

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
        return [MetadataProfile(self, data) for data in self._raw.get_metadataProfile()]
