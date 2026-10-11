from abc import abstractmethod

from arrapi.objs.base import BaseObj

_DEFAULT_PAGE_SIZE = 250


def _paginate(paged_getter, page_size=_DEFAULT_PAGE_SIZE):
    """Yield every record returned by a Sonarr or Radarr ``/paged`` endpoint."""
    page = 1
    seen = 0
    while True:
        response = paged_getter(page=page, pageSize=page_size) or {}
        records = response.get("records", [])
        yield from records
        seen += len(records)
        total_records = response.get("totalRecords")
        if total_records is not None:
            if seen >= total_records:
                return
        elif len(records) < page_size:
            return
        page += 1


class SimpleObj(BaseObj):
    @abstractmethod
    def _load(self, data):
        super()._load(data)


class Queue(SimpleObj):
    """Represents a Sonarr or Radarr download-queue item.

        Attributes:
            id (int): Queue item ID.
            title (str): Release title.
            status (str): Current queue status.
            protocol (str): Download protocol.
            downloadId (str): Download client item ID.
            errorMessage (str): Error reported for this item, if any.
    """

    @classmethod
    def get_all(cls, arr):
        if not arr._raw.new_codebase:
            return [cls(arr, data) for data in arr._raw.get_queue()]
        return [cls(arr, data) for data in _paginate(arr._raw.get_queue)]

    def _load(self, data):
        super()._load(data)
        self.id = self._parse(attrs="id", value_type="int", default_is_none=True)
        self.title = self._parse(attrs="title")
        self.status = self._parse(attrs="status")
        self.protocol = self._parse(attrs="protocol")
        self.downloadId = self._parse(attrs="downloadId")
        self.errorMessage = self._parse(attrs="errorMessage")
        self._finish(self.title)

    def remove(self, remove_from_client=True, blocklist=False, skip_redownload=False,
               change_category=False):
        """Remove this item from the Arr queue and optionally its download client."""
        return self._raw.delete_queue_id(
            self.id, removeFromClient=remove_from_client, blocklist=blocklist,
            skipRedownload=skip_redownload, changeCategory=change_category
        )


class Episode(SimpleObj):
    """Represents a Sonarr episode.

        Attributes:
            id (int): Episode ID.
            seriesId (int): Parent series ID.
            seasonNumber (int): Season number.
            episodeNumber (int): Episode number.
            title (str): Episode title.
            monitored (bool): Whether Sonarr monitors this episode.
            hasFile (bool): Whether a file is present.
            series (Series): Parent series when requested from the calendar with ``include_series``.
            episodeFile (dict): Episode file details when requested with ``include_episode_file``.
            images (List[Image]): Episode artwork when requested with ``include_episode_images``.
    """

    def _load(self, data):
        super()._load(data)
        self.id = self._parse(attrs="id", value_type="int", default_is_none=True)
        self.seriesId = self._parse(attrs="seriesId", value_type="int")
        self.seasonNumber = self._parse(attrs="seasonNumber", value_type="int")
        self.episodeNumber = self._parse(attrs="episodeNumber", value_type="int")
        self.title = self._parse(attrs="title")
        self.monitored = self._parse(attrs="monitored", value_type="bool")
        self.hasFile = self._parse(attrs="hasFile", value_type="bool")
        if "series" in self._data:
            from arrapi.objs.reload import Series
            self.series = Series(self._arr, data=self._data["series"])
        if "episodeFile" in self._data:
            self.episodeFile = self._parse(attrs="episodeFile", value_type="dict")
        if "images" in self._data:
            self.images = self._parse(attrs="images", value_type="image", is_list=True)
        self._finish(self.title)

    def monitor(self, monitored=True):
        """Set whether Sonarr monitors this episode."""
        self._raw.put_episode_monitor([self.id], monitored)
        self._load({**self._data, "monitored": monitored})


class Collection(SimpleObj):
    """ Represents a single Collection.

        Attributes:
            name (str): Name of the Collection.
            tmdbId (int): TMDb Collection ID of the Collection.
    """

    def _load(self, data):
        super()._load(data)
        self.name = self._parse(attrs="name")
        self.tmdbId = self._parse(attrs="tmdbId", value_type="int")
        self._finish(self.name)

    def get_url(self):
        """ URL of the Collection on TMDb"""
        return f"https://www.themoviedb.org/collection/{self.tmdbId}"


class Image(SimpleObj):
    """ Represents a single Image.

        Attributes:
            coverType (str): Cover Type of the Image.
            url (str): URL of the Image.
            remoteUrl (str): Remote URL of the Image.
    """

    def _load(self, data):
        super()._load(data)
        self.coverType = self._parse(attrs="coverType")
        self.url = self._parse(attrs="url")
        self.remoteUrl = self._parse(attrs="remoteUrl")
        self._finish(self.remoteUrl)


class MetadataProfile(SimpleObj):
    """ Represents a single Metadata Profile.

        Attributes:
            id (int): ID of the Metadata Profile.
            name (str): Name of the Metadata Profile.
    """

    def _load(self, data):
        super()._load(data)
        self.id = self._parse(attrs="id", value_type="int")
        self.name = self._parse(attrs="name")
        self._finish(self.name)

class RemotePathMapping(SimpleObj):
    """ Represents a single Remote Path Mapping.

        Attributes:
            id (int): ID of the Remote Path Mapping.
            host (str): Host of the Remote Path Mapping.
            localPath (str): Local Path of the Remote Path Mapping.
            remotePath (str): Remote Path of the Remote Path Mapping.
    """

    def _load(self, data):
        super()._load(data)
        self.id = self._parse(attrs="id", value_type="int")
        self.host = self._parse(attrs="host")
        self.remotePath = self._parse(attrs="remotePath")
        self.localPath = self._parse(attrs="localPath")
        self._finish(self.host)

class RootFolder(SimpleObj):
    """ Represents a single Root Folder.

        Attributes:
            id (int): ID of the Root Folder.
            path (str): Path of the Root Folder.
            freeSpace (int): Free Space in the Root Folder.
            name (str): Name of the Root Folder. (Only when loaded using :class:`~arrapi.apis.lidarr.LidarrAPI` or :class:`~arrapi.apis.readarr.ReadarrAPI`)
            defaultMetadataProfileId (int): Default Metadata Profile ID of the Root Folder. (Only when loaded using :class:`~arrapi.apis.lidarr.LidarrAPI` or :class:`~arrapi.apis.readarr.ReadarrAPI`)
            defaultQualityProfileId (int): Default Quality Profile ID of the Root Folder. (Only when loaded using :class:`~arrapi.apis.lidarr.LidarrAPI` or :class:`~arrapi.apis.readarr.ReadarrAPI`)
            defaultMonitorOption (int): Default Monitor Option of the Root Folder. (Only when loaded using :class:`~arrapi.apis.lidarr.LidarrAPI` or :class:`~arrapi.apis.readarr.ReadarrAPI`)
            defaultTags (int): Default Tags of the Root Folder. (Only when loaded using :class:`~arrapi.apis.lidarr.LidarrAPI` or :class:`~arrapi.apis.readarr.ReadarrAPI`)
            isCalibreLibrary (bool): If the Root Folder is a Calibre Library. (Only when loaded using :class:`~arrapi.apis.readarr.ReadarrAPI`)
            unmappedFolders (List[UnmappedFolder]): Unmapped Folders in the Root Folder. (Only when loaded using :class:`~arrapi.apis.radarr.SonarrAPI` V3 or :class:`~arrapi.apis.radarr.RadarrAPI` V3)
    """

    def _load(self, data):
        super()._load(data)
        self.path = self._parse(attrs="path")
        self.id = self._parse(attrs="id", value_type="int")
        if "name" in self._data:
            self.name = self._parse(attrs="name")
        if "defaultMetadataProfileId" in self._data:
            self.defaultMetadataProfileId = self._parse(attrs="defaultMetadataProfileId", value_type="int")
        if "defaultQualityProfileId" in self._data:
            self.defaultQualityProfileId = self._parse(attrs="defaultQualityProfileId", value_type="int")
        if "defaultMonitorOption" in self._data:
            self.defaultMonitorOption = self._parse(attrs="defaultMonitorOption", value_type="str")
        if "defaultTags" in self._data:
            self.defaultTags = self._parse(attrs="defaultTags", value_type="int", is_list=True)
        if "isCalibreLibrary" in self._data:
            self.isCalibreLibrary = self._parse(attrs="isCalibreLibrary", value_type="bool")
        self.freeSpace = self._parse(attrs="freeSpace", value_type="int")
        if "unmappedFolders" in self._data:
            self.unmappedFolders = [UnmappedFolder(self._arr, folder) for folder in self._data["unmappedFolders"]]
        self._finish(self.name if "name" in self._data else self.path)

    def delete(self):
        self._raw.delete_rootFolder(self.id)

class Season(SimpleObj):
    """ Represents a single Season.

        Attributes:
            seasonNumber (int): Season Number of the Tag.
            monitored (bool): If the Season is monitored.
            totalEpisodeCount (int): Total Episode Count for the Season.
            episodeCount (int): Episode Count for the Season.
            episodeFileCount (int): Episode File Count for the Season.
            sizeOnDisk (int): Size on Disk for the Season.
            percentOfEpisodes (float): Percent of Episodes for the Season..
            nextAiring (datetime): Next Airing Date for an Episode of this Season.
            previousAiring (datetime): Previous Airing Date for the latest Episode of this Season.
    """

    def _load(self, data):
        super()._load(data)
        self.seasonNumber = self._parse(attrs="seasonNumber", value_type="int")
        self.monitored = self._parse(attrs="monitored", value_type="bool")
        if "statistics" in self._data:
            self.totalEpisodeCount = self._parse(attrs=["statistics", "totalEpisodeCount"], value_type="int")
            self.episodeCount = self._parse(attrs=["statistics", "episodeCount"], value_type="int")
            self.episodeFileCount = self._parse(attrs=["statistics", "episodeFileCount"], value_type="int")
            self.sizeOnDisk = self._parse(attrs=["statistics", "sizeOnDisk"], value_type="int")
            self.percentOfEpisodes = self._parse(attrs=["statistics", "percentOfEpisodes"], value_type="float")
            self.nextAiring = self._parse(attrs="nextAiring", value_type="date")
            self.previousAiring = self._parse(attrs="previousAiring", value_type="date")
        self._finish(f"Season {self.seasonNumber}")


class UnmappedFolder(SimpleObj):
    """ Represents a single Unmapped Folder.

        Attributes:
            name (str): Name of the Unmapped Folder.
            path (str): Path of the Unmapped Folder.
    """

    def _load(self, data):
        super()._load(data)
        self.name = self._parse(attrs="name")
        self.path = self._parse(attrs="path")
        self._finish(self.path)

class RadarrExclusion(SimpleObj):
    """ Represents a single Radarr Exclusion.

        Attributes:
            tmdbId (int): TMDb ID of the Excluded Movie.
            title (str): Title of the Excluded Movie.
            year (int): Year of the Excluded Movie.
    """

    @classmethod
    def get_all(cls, arr):
        """Return every Radarr Import List Exclusion.

        Uses the paged endpoint on the modern codebase and the legacy flat
        endpoint otherwise.
        """
        if not arr._raw.new_codebase:
            return [cls(arr, data) for data in arr._raw.get_exclusions()]
        return [cls(arr, data) for data in _paginate(arr._raw.get_exclusions_paged)]

    def _load(self, data):
        super()._load(data)
        self.tmdbId = self._parse(attrs="tmdbId", value_type="int")
        self.title = self._parse(attrs="movieTitle")
        self.year = self._parse(attrs="movieYear", value_type="int")
        self._finish(f"TMDb ID: {self.tmdbId}")

class SonarrExclusion(SimpleObj):
    """ Represents a single Sonarr Exclusion.

        Attributes:
            tvdbId (int): TVDb ID of the Excluded Series.
            title (str): Title of the Excluded Series.
    """

    @classmethod
    def get_all(cls, arr):
        """Return every Sonarr Import List Exclusion.

        Uses the paged endpoint on the modern codebase and the legacy flat
        endpoint otherwise.
        """
        if not arr._raw.new_codebase:
            return [cls(arr, data) for data in arr._raw.get_importlistexclusion()]
        return [cls(arr, data) for data in _paginate(arr._raw.get_importlistexclusion_paged)]

    def _load(self, data):
        super()._load(data)
        self.tvdbId = self._parse(attrs="tvdbId", value_type="int")
        self.title = self._parse(attrs="title")
        self._finish(f"TVDb ID: {self.tvdbId}")
