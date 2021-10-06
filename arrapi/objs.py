from arrapi import util
from typing import Optional, Union, List
from .exceptions import Exists, Invalid, NotFound


class BaseArr:
    """ Base Class for Arr Objects.

        Attributes:
            id (int): ID of the Object.
    """

    def __init__(self, data=None):
        self._loading = True
        self._data = data
        self.id = None
        self._name = None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"[{self.id}:{self._name}]" if self.id is not None else f"[{self._name}]"

    def __eq__(self, other):
        if type(self) is type(other):
            if self.id is None and other.id is None:
                return self._name == other._name
            elif self.id is not None and other.id is not None:
                return self.id == other.id
            else:
                return False
        elif isinstance(other, int) and self.id is not None:
            return self.id == other
        else:
            return str(self._name) == str(other)

    def __setattr__(self, key, value):
        if key not in ["_loading"] and self._loading is False:
            raise AttributeError("Attributes cannot be edited")
        else:
            self.__dict__[key] = value

    def __delattr__(self, key):
        raise AttributeError("Attributes cannot be deleted")


class QualityProfile(BaseArr):
    """ Represents a single Quality Profile.

        Attributes:
            id (int): ID of the Quality Profile.
            name (str): Name of the Quality Profile.
    """

    def __init__(self, arr, data):
        super().__init__(data=data)
        self._arr = arr
        self.name = util.parse(self._data, attribute="name")
        self._name = self.name
        self.id = util.parse(self._data, attribute="id", value_type="int")
        self._loading = False


class MetadataProfile(BaseArr):
    """ Represents a single Metadata Profile.

        Attributes:
            id (int): ID of the Metadata Profile.
            name (str): Name of the Metadata Profile.
    """

    def __init__(self, arr, data):
        super().__init__(data=data)
        self._arr = arr
        self.name = util.parse(self._data, attribute="name")
        self._name = self.name
        self.id = util.parse(self._data, attribute="id", value_type="int")
        self._loading = False


class LanguageProfile(BaseArr):
    """ Represents a single Language Profile.

        Attributes:
            id (int): ID of the Language Profile.
            name (str): Name of the Language Profile.
    """

    def __init__(self, sonarr, data):
        super().__init__(data=data)
        self._sonarr = sonarr
        self.name = util.parse(self._data, attribute="name")
        self._name = self.name
        self.id = util.parse(self._data, attribute="id", value_type="int")
        self._loading = False


class RemotePathMapping(BaseArr):
    """ Represents a single Remote Path Mapping.

        Attributes:
            id (int): ID of the Remote Path Mapping.
            host (str): Host of the Remote Path Mapping.
            localPath (str): Local Path of the Remote Path Mapping.
            remotePath (str): Remote Path of the Remote Path Mapping.
    """

    def __init__(self, arr, data):
        super().__init__(data=data)
        self._arr = arr
        self.host = util.parse(self._data, attribute="host")
        self._name = self.host
        self.remotePath = util.parse(self._data, attribute="remotePath")
        self.localPath = util.parse(self._data, attribute="localPath")
        self.id = util.parse(self._data, attribute="id", value_type="int")
        self._loading = False


class RootFolder(BaseArr):
    """ Represents a single Root Folder.

        Attributes:
            id (int): ID of the Root Folder.
            path (str): Path of the Root Folder.
            freeSpace (int): Free Space in the Root Folder.
            name (str): Name of the Root Folder. (Only when loaded using :class:`~arrapi.lidarr.LidarrAPI` or :class:`~arrapi.readarr.ReadarrAPI`)
            defaultMetadataProfileId (int): Default Metadata Profile ID of the Root Folder. (Only when loaded using :class:`~arrapi.lidarr.LidarrAPI` or :class:`~arrapi.readarr.ReadarrAPI`)
            defaultQualityProfileId (int): Default Quality Profile ID of the Root Folder. (Only when loaded using :class:`~arrapi.lidarr.LidarrAPI` or :class:`~arrapi.readarr.ReadarrAPI`)
            defaultMonitorOption (int): Default Monitor Option of the Root Folder. (Only when loaded using :class:`~arrapi.lidarr.LidarrAPI` or :class:`~arrapi.readarr.ReadarrAPI`)
            defaultTags (int): Default Tags of the Root Folder. (Only when loaded using :class:`~arrapi.lidarr.LidarrAPI` or :class:`~arrapi.readarr.ReadarrAPI`)
            isCalibreLibrary (bool): If the Root Folder is a Calibre Library. (Only when loaded using :class:`~arrapi.readarr.ReadarrAPI`)
            unmappedFolders (List[UnmappedFolder]): Unmapped Folders in the Root Folder. (Only when loaded using :class:`~arrapi.radarr.SonarrAPI` V3 or :class:`~arrapi.radarr.RadarrAPI` V3)
    """

    def __init__(self, arr, data):
        super().__init__(data=data)
        self._arr = arr
        self.path = util.parse(self._data, attribute="path")
        if "name" in self._data:
            self.name = util.parse(self._data, attribute="name")
            self._name = self.name
        else:
            self._name = self.path
        if "defaultMetadataProfileId" in self._data:
            self.defaultMetadataProfileId = util.parse(self._data, attribute="defaultMetadataProfileId", value_type="int")
        if "defaultQualityProfileId" in self._data:
            self.defaultQualityProfileId = util.parse(self._data, attribute="defaultQualityProfileId", value_type="int")
        if "defaultMonitorOption" in self._data:
            self.defaultMonitorOption = util.parse(self._data, attribute="defaultMonitorOption", value_type="str")
        if "defaultTags" in self._data:
            self.defaultTags = util.parse(self._data, attribute="defaultTags", value_type="intList")
        if "isCalibreLibrary" in self._data:
            self.isCalibreLibrary = util.parse(self._data, attribute="isCalibreLibrary", value_type="bool")
        self.freeSpace = util.parse(self._data, attribute="freeSpace", value_type="int")
        if "unmappedFolders" in self._data:
            self.unmappedFolders = [UnmappedFolder(self._arr, folder) for folder in self._data["unmappedFolders"]]
        self.id = util.parse(self._data, attribute="id", value_type="int")
        self._loading = False


class UnmappedFolder(BaseArr):
    """ Represents a single Unmapped Folder.

        Attributes:
            name (str): Name of the Unmapped Folder.
            path (str): Path of the Unmapped Folder.
    """

    def __init__(self, arr, data):
        super().__init__(data=data)
        self._arr = arr
        self.name = util.parse(self._data, attribute="name")
        self.path = util.parse(self._data, attribute="path")
        self._name = self.path
        self._loading = False


class SystemStatus(BaseArr):
    """ Represents the System Status.

        Attributes:
            version (str): Version of the Arr Instance.

        Check dir(SystemStatus) for all attribute as the rest are auto built.
    """

    def __init__(self, arr):
        super().__init__()
        self._arr = arr
        self._load()

    def _load(self):
        self._loading = True
        self.version = None
        self._data = self._arr._get_system_status()
        for key, value in self._data.items():
            if key.startswith("is"):
                setattr(self, key, util.parse(value, value_type="int"))
            elif key.endswith("Time"):
                setattr(self, key, util.parse(value, value_type="date"))
            elif key == "migrationVersion":
                setattr(self, key, util.parse(value, value_type="int"))
            elif key == "version":
                self.version = value
                self._name = self.version
            else:
                setattr(self, key, value)
        self._loading = False

    def reload(self) -> None:
        for key in self._data:
            delattr(self, key)
        self._load()


class Tag(BaseArr):
    """ Represents a single Tag.

        Attributes:
            id (int): ID of the Tag.
            label (str): Label of the Tag.
            detail (bool): If the Tag was loaded with details.
            delayProfileIds (List[int]): Delay Profile IDs. (Only when loaded with details)
            notificationIds (List[int]): Notification IDs. (Only when loaded with details)
            restrictionIds (List[int]): Restriction IDs. (Only when loaded with details)
            importListIds (List[int]): Import List IDs. (Only when loaded with details)
            movieIds (List[int]): Radarr Movie IDs. (Only when loaded with details using :class:`~arrapi.radarr.RadarrAPI`)
            seriesIds (List[int]): Sonarr Series IDs. (Only when loaded with details using :class:`~arrapi.radarr.SonarrAPI`)
            artistIds (List[int]): Lidarr Artist IDs. (Only when loaded with details using :class:`~arrapi.lidarr.LidarrAPI`)
            authorIds (List[int]): Readarr Author IDs. (Only when loaded with details using :class:`~arrapi.readarr.ReadarrAPI`)
    """

    def __init__(self, arr, data):
        super().__init__()
        self._arr = arr
        self._load(data)

    def _load(self, data):
        self._loading = True
        self._data = data
        self.label = util.parse(data, attribute="label")
        self._name = self.label
        self.id = util.parse(data, attribute="id", value_type="int", default_is_none=True)
        self.detail = False
        if "delayProfileIds" in data:
            self.detail = True
            self.delayProfileIds = util.parse(data, attribute="delayProfileIds", value_type="intList")
            self.notificationIds = util.parse(data, attribute="notificationIds", value_type="intList")
            self.restrictionIds = util.parse(data, attribute="restrictionIds", value_type="intList")
            self.importListIds = util.parse(data, attribute="importListIds", value_type="intList")
        if "movieIds" in data:
            self.movieIds = util.parse(data, attribute="movieIds", value_type="intList")
        if "seriesIds" in data:
            self.seriesIds = util.parse(data, attribute="seriesIds", value_type="intList")
        if "artistIds" in data:
            self.artistIds = util.parse(data, attribute="artistIds", value_type="intList")
        if "authorIds" in data:
            self.authorIds = util.parse(data, attribute="authorIds", value_type="intList")
        self._loading = False

    def reload(self, detail: bool = False) -> None:
        """ Reload the :class:`~arrapi.objs.Tag`.

            Parameters:
                detail (bool): Reload tag with details.
        """
        self._load(self._arr._get_tag_id(self.id, detail=self.detail if detail is None else detail))

    def edit(self, label: str) -> None:
        """ Edit the :class:`~arrapi.objs.Tag`.

            Parameters:
                label (str): Label to change tag to.

        """
        self._load(self._arr.edit_tag(self.id, label))

    def delete(self) -> None:
        """ Delete the :class:`~arrapi.objs.Tag`."""
        self._arr.delete_tag(self.id)


class Movie(BaseArr):
    """ Represents a single Movie.

        Attributes:
            id (int): ID of the Movie.
            title (str): Title of the Movie.
            sortTitle (str): Sort Title of the Movie.
            sizeOnDisk (int): Movie Size On Disk.
            status (str): Status of the Movie.
            overview (str): Overview of the Movie.
            inCinemas (datetime): Date the Movie was in Cinemas.
            physicalRelease (datetime): Date the Movie was Physically Released.
            website (str): Website of the Movie.
            year (int): Year of the Movie.
            hasFile (bool): If the Movie has a file.
            youTubeTrailerId (str): YouTube Trailer ID for the Movie.
            studio (str): Studio of the Movie.
            path (str): Path of the Movie.
            monitored (bool): If the Movie is monitored.
            minimumAvailability (str): Minimum Availability of the Movie.
            isAvailable (bool): If the Movie is Available.
            folderName (str): Folder Name of the Movie.
            runtime (int): Runtime of the Movie.
            cleanTitle (str): Clean Title of the Movie.
            imdbId (str): IMDb ID of the Movie.
            tmdbId (int): TMDb ID of the Movie.
            titleSlug (str): Title Slug of the Movie.
            certification (str): Certification of the Movie.
            genres (List[str]): List of genres for the Movie.
            tags (List[int]): List of tag ids for the Movie.
            rating_votes (int): Number of votes for the Movie.
            rating_value (float): Rating of the Movie.
            originalTitle (str): Original Title of the Movie. (Radarr v3 Only)
            digitalRelease (datetime): Date the Movie was Released Digitally. (Radarr v3 Only)
            qualityProfileId (int): Quality Profile of the Movie. (Radarr v3 Only)
            collection_name (str): Collection Name of the Movie. (Radarr v3 Only)
            collection_tmdbId (int): TMDb Collection ID for the Movie. (Radarr v3 Only)
            downloaded (bool): If the Movie has been Downloaded. (Radarr v2 Only)
            profileId (int): Quality Profile of the Movie. (Radarr v2 Only)
    """

    def __init__(self, radarr, data=None, movie_id=None, tmdb_id=None, imdb_id=None):
        super().__init__()
        self._radarr = radarr
        self._load(load_data=data, movie_id=movie_id, tmdb_id=tmdb_id, imdb_id=imdb_id)

    def _load(self, load_data=None, movie_id=None, tmdb_id=None, imdb_id=None):
        if load_data is not None:
            data = load_data
        elif movie_id is not None:
            data = self._radarr._get_movie_id(movie_id)
        elif tmdb_id is not None or imdb_id is not None:
            items = self._radarr._get_movie_lookup(f"tmdb:{tmdb_id}" if tmdb_id is not None else f"imdb:{imdb_id}")
            if items:
                data = items[0]
            else:
                raise NotFound("Item Not Found")
        else:
            raise Invalid("Load Failed: No Load Input")
        self._loading = True
        self._data = data
        self.title = util.parse(data, attribute="title")
        self._name = self.title
        self.sortTitle = util.parse(data, attribute="sortTitle")
        self.sizeOnDisk = util.parse(data, attribute="sizeOnDisk", value_type="int")
        self.status = util.parse(data, attribute="status")
        self.overview = util.parse(data, attribute="overview")
        self.inCinemas = util.parse(data, attribute="inCinemas", value_type="date")
        self.physicalRelease = util.parse(data, attribute="physicalRelease", value_type="date")
        self.website = util.parse(data, attribute="website")
        self.year = util.parse(data, attribute="year", value_type="int")
        self.hasFile = util.parse(data, attribute="hasFile", value_type="bool")
        self.youTubeTrailerId = util.parse(data, attribute="youTubeTrailerId")
        self.studio = util.parse(data, attribute="studio")
        self.path = util.parse(data, attribute="path")
        self.monitored = util.parse(data, attribute="monitored", value_type="bool")
        self.minimumAvailability = util.parse(data, attribute="minimumAvailability")
        self.isAvailable = util.parse(data, attribute="isAvailable", value_type="bool")
        self.folderName = util.parse(data, attribute="folderName")
        self.runtime = util.parse(data, attribute="runtime", value_type="int")
        self.cleanTitle = util.parse(data, attribute="cleanTitle")
        self.imdbId = util.parse(data, attribute="imdbId")
        self.tmdbId = util.parse(data, attribute="tmdbId", value_type="int", default_is_none=True)
        self.titleSlug = util.parse(data, attribute="titleSlug")
        self.certification = util.parse(data, attribute="certification")
        self.genres = util.parse(data, attribute="genres", value_type="strList")
        self.tags = util.parse(data, attribute="tags", value_type="intList")
        self.rating_votes = util.parse(data["rating"], attribute="votes", value_type="int") if "rating" in data else 0
        self.rating_value = util.parse(data["rating"], attribute="value", value_type="float") if "rating" in data else 0
        self.id = util.parse(data, attribute="id", value_type="int", default_is_none=True)

        if self._radarr.v3:
            self.originalTitle = util.parse(data, attribute="originalTitle")
            self.digitalRelease = util.parse(data, attribute="digitalRelease", value_type="date")
            self.qualityProfileId = util.parse(data, attribute="qualityProfileId", value_type="int")
            self.collection_name = util.parse(data["collection"], attribute="name") if "collection" in data else None
            self.collection_tmdbId = util.parse(data["collection"], attribute="tmdbId", value_type="int",
                                                default_is_none=True) if "collection" in data else None
        else:
            self.downloaded = util.parse(data, attribute="downloaded", value_type="bool")
            self.profileId = util.parse(data, attribute="profileId", value_type="int")
        self._loading = False

    def reload(self) -> None:
        """ Reloads the Movie Object. """
        self._load(movie_id=self.id, tmdb_id=self.tmdbId, imdb_id=self.imdbId)

    def _get_add_data(self, options):
        if self.id:
            raise Exists(f"{self.title} is already in Radarr")
        self._data["monitored"] = options["monitor"]
        self._data["rootFolderPath"] = options["root_folder"]
        self._data["qualityProfileId" if self._radarr.v3 else "profileId"] = options["quality_profile"]
        self._data["minimumAvailability"] = options["minimum_availability"]
        self._data["addOptions"] = {"searchForMovie": options["search"]}
        if "tags" in options:
            self._data["tags"] = options["tags"]
        return self._data

    def add(self,
            root_folder: Union[str, int, RootFolder],
            quality_profile: Union[str, int, QualityProfile],
            monitor: bool = True,
            search: bool = True,
            minimum_availability: str = "announced",
            tags: Optional[List[Union[str, int, Tag]]] = None
            ) -> None:
        """ Add this Movie to Radarr.

            Parameters:
                root_folder (Union[str, int, RootFolder]): Root Folder for the Movie.
                quality_profile (Union[str, int, QualityProfile]): Quality Profile for the Movie.
                monitor (bool): Monitor the Movie.
                search (bool): Search for the Movie after adding.
                minimum_availability (str): Minimum Availability for the Movie. Valid options are announced, inCinemas, released, or preDB.
                tags (Optional[List[Union[str, int, Tag]]]): Tags to be added to the Movie.

            Raises:
                :class:`~arrapi.exceptions.Invalid`: When one of the options given is invalid.
                :class:`~arrapi.exceptions.Exists`: When the Movie already Exists in Radarr.
        """
        options = self._radarr._validate_add_options(root_folder, quality_profile, monitor=monitor, search=search,
                                                     minimum_availability=minimum_availability, tags=tags)
        self._load(load_data=self._radarr._post_movie(self._get_add_data(options)))

    def edit(self,
             path: Optional[str] = None,
             move_files: bool = False,
             quality_profile: Optional[Union[str, int, QualityProfile]] = None,
             monitored: Optional[bool] = None,
             minimum_availability: Optional[str] = None,
             tags: Optional[List[Union[str, int, Tag]]] = None,
             apply_tags: str = "add"
             ) -> None:
        """ Edit this Movie in Radarr.

            Parameters:
                path (Optional[str]): Path to change the Movie to.
                move_files (bool): When changing the path do you want to move the files to the new path.
                quality_profile (Optional[Union[str, int, QualityProfile]]): Quality Profile to change the Movie to.
                monitored (Optional[bool]): Monitor the Movie.
                minimum_availability (Optional[str]): Minimum Availability to change the Movie to. Valid options are announced, inCinemas, released, or preDB.
                tags (Optional[List[Union[str, int, Tag]]]): Tags to be added, replaced, or removed from the Movie.
                apply_tags (str): How you want to edit the Tags. Valid options are add, replace, or remove.

            Raises:
                :class:`ValueError`: When theres no options given.
                :class:`~arrapi.exceptions.Invalid`: When one of the options given is invalid.
                :class:`~arrapi.exceptions.NotFound`: When the Movie isn't found in Radarr and must be added to Radarr before editing.
        """
        if not self.id:
            raise NotFound(f"{self.title} not found Radarr Sonarr it must be added before editing")
        options = self._radarr._validate_edit_options(path=path, move_files=move_files, quality_profile=quality_profile,
                                                      monitored=monitored, minimum_availability=minimum_availability,
                                                      tags=tags, apply_tags=apply_tags)
        valid_move_files = options["path"] if "path" in options else False
        for key, value in options.items():
            if key == "tags":
                tag_type = options["apply_tags"]
                if tag_type == "add":
                    self._data[key].extend([t for t in value if t not in self._data["tags"]])
                elif tag_type == "remove":
                    self._data[key] = [t for t in self._data["tags"] if t not in value]
                elif tag_type == "replace":
                    self._data[key] = value
                else:
                    raise Invalid(f"Invalid apply_tags: '{tag_type}' Options: {self._radarr.apply_tag_options}")
            elif key != ["applyTags", "moveFiles"]:
                self._data[key] = value
        self._load(load_data=self._radarr._put_movie_id(self.id, self._data, moveFiles=valid_move_files))

    def delete(self, addImportExclusion: bool = False, deleteFiles: bool = False) -> None:
        """ Delete this Movie from Radarr.

            Parameters:
                addImportExclusion (bool): Add Import Exclusion for this Movie.
                deleteFiles (bool): Delete Files for this Movie.

            Raises:
                :class:`~arrapi.exceptions.NotFound`: When the Movie isn't found in Radarr.
        """
        self._radarr._delete_movie_id(self.id, addImportExclusion=addImportExclusion, deleteFiles=deleteFiles)
        self._loading = True
        self.id = None
        self._loading = False


class Series(BaseArr):
    """ Represents a single Series.

        Attributes:
            id (int): ID of the Series.
            title (str): Title of the Series.
            sortTitle (str): Sort Title of the Series.
            status (str): Status of the Series.
            overview (str): Overview of the Series.
            seasons (List[:class:`~arrapi.objs.Season`]): List of Seasons in the Series.
            nextAiring (datetime): Date the next Episode in the Series Airs.
            previousAiring (datetime): Date the latest Episode in the Series Aired.
            network (str): Network the Series Airs on.
            airTime (str): Time Series Airs.
            year (int): Year of the Series.
            path (str): Path of the Series.
            languageProfileId (int): Language Profile of the Series.
            seasonFolder (bool): If the Series has Season Folders.
            monitored (bool): If the Series is monitored.
            useSceneNumbering (bool): If the Series uses Scene Numbering.
            runtime (int): Runtime of the Series.
            cleanTitle (str): Clean Title of the Series.
            imdbId (str): IMDb ID of the Series.
            tvdbId (int): TVDb ID of the Series.
            tvRageId (int): TV Rage ID of the Series.
            tvMazeId (int): TV Maze ID of the Series.
            titleSlug (str): Title Slug of the Series.
            firstAired (datetime): Date the Series First Aired.
            seriesType (str): Series Type of the Series.
            certification (str): Certification of the Series.
            genres (List[str]): List of genres for the Series.
            tags (List[int]): List of tag ids for the Series.
            rating_votes (int): Number of votes for the Series.
            rating_value (float): Rating of the Series.
            seasonCount (int): Number of Seasons in the Series.
            totalEpisodeCount (int): Total Episodes in the Series.
            episodeCount (int): Episodes in the Series.
            episodeFileCount (int): Episode File Count for the Series.
            sizeOnDisk (int): Size on Disk for the Series.
            ended (bool): If the Series has ended. (Sonarr v3 Only)
            rootFolderPath (str): Root Folder Path for the Series. (Sonarr v3 Only)
            qualityProfileId (int): Quality Profile of the Series. (Sonarr v3 Only)
            percentOfEpisodes (float): Percent of Episodes obtained. (Sonarr v3 Only)
            profileId (int): Quality Profile of the Series. (Sonarr v2 Only)
    """

    def __init__(self, sonarr, data=None, series_id=None, tvdb_id=None):
        super().__init__()
        self._sonarr = sonarr
        self._data = None
        self._load(load_data=data, series_id=series_id, tvdb_id=tvdb_id)

    def _load(self, load_data=None, series_id=None, tvdb_id=None):
        if load_data is not None:
            data = load_data
        elif series_id is not None:
            data = self._sonarr._get_series_id(series_id)
        elif tvdb_id is not None:
            items = self._sonarr._get_series_lookup(f"tvdb:{tvdb_id}")
            if items:
                data = items[0]
            else:
                raise NotFound("Item Not Found")
        else:
            raise Invalid("Load Failed: No Load Input")
        self._loading = True
        self._data = data
        self.title = util.parse(data, attribute="title")
        self._name = self.title
        self.sortTitle = util.parse(data, attribute="sortTitle")
        self.status = util.parse(data, attribute="status")
        self.overview = util.parse(data, attribute="overview")
        self.nextAiring = util.parse(data, attribute="nextAiring", value_type="date")
        self.previousAiring = util.parse(data, attribute="previousAiring", value_type="date")
        self.network = util.parse(data, attribute="network")
        self.airTime = util.parse(data, attribute="airTime")
        self.year = util.parse(data, attribute="year", value_type="int")
        self.path = util.parse(data, attribute="path")
        self.languageProfileId = util.parse(data, attribute="languageProfileId", value_type="int")
        self.seasonFolder = util.parse(data, attribute="seasonFolder", value_type="bool")
        self.monitored = util.parse(data, attribute="monitored", value_type="bool")
        self.useSceneNumbering = util.parse(data, attribute="useSceneNumbering", value_type="bool")
        self.runtime = util.parse(data, attribute="runtime", value_type="int")
        self.cleanTitle = util.parse(data, attribute="cleanTitle")
        self.imdbId = util.parse(data, attribute="imdbId")
        self.tvdbId = util.parse(data, attribute="tvdbId", value_type="int")
        self.tvRageId = util.parse(data, attribute="tvRageId", value_type="int")
        self.tvMazeId = util.parse(data, attribute="tvMazeId", value_type="int")
        self.titleSlug = util.parse(data, attribute="titleSlug")
        self.firstAired = util.parse(data, attribute="firstAired", value_type="date")
        self.seriesType = util.parse(data, attribute="seriesType")
        self.certification = util.parse(data, attribute="certification")
        self.genres = util.parse(data, attribute="genres", value_type="strList")
        self.tags = util.parse(data, attribute="tags", value_type="intList")
        if "rating" in data:
            self.rating_votes = util.parse(data["rating"], attribute="votes", value_type="int")
            self.rating_value = util.parse(data["rating"], attribute="value", value_type="float")
        self.id = util.parse(data, attribute="id", value_type="int", default_is_none=True)
        self.seasons = [Season(self._sonarr, s) for s in data["seasons"]]

        if self._sonarr.v3:
            self.ended = util.parse(data, attribute="ended", value_type="bool")
            self.rootFolderPath = util.parse(data, attribute="rootFolderPath")
            self.qualityProfileId = util.parse(data, attribute="qualityProfileId", value_type="int")
            if "statistics" in data:
                stats = data["statistics"]
                self.seasonCount = util.parse(stats, attribute="seasonCount", value_type="int")
                self.totalEpisodeCount = util.parse(stats, attribute="totalEpisodeCount", value_type="int")
                self.episodeCount = util.parse(stats, attribute="episodeCount", value_type="int")
                self.episodeFileCount = util.parse(stats, attribute="episodeFileCount", value_type="int")
                self.sizeOnDisk = util.parse(stats, attribute="sizeOnDisk", value_type="int")
                self.percentOfEpisodes = util.parse(stats, attribute="percentOfEpisodes", value_type="float")
        else:
            self.profileId = util.parse(data, attribute="profileId", value_type="int")
            self.seasonCount = util.parse(data, attribute="seasonCount", value_type="int")
            self.totalEpisodeCount = util.parse(data, attribute="totalEpisodeCount", value_type="int")
            self.episodeCount = util.parse(data, attribute="episodeCount", value_type="int")
            self.episodeFileCount = util.parse(data, attribute="episodeFileCount", value_type="int")
            self.sizeOnDisk = util.parse(data, attribute="sizeOnDisk", value_type="int")
        self._loading = False

    def reload(self) -> None:
        """ Reloads the Movie Object. """
        self._load(series_id=self.id, tvdb_id=self.tvdbId)

    def _get_add_data(self, options):
        if self.id:
            raise Exists(f"{self.title} is already in Sonarr")
        self._data["rootFolderPath"] = options["root_folder"]
        self._data["monitored"] = options["monitored"]
        self._data["qualityProfileId" if self._sonarr.v3 else "profileId"] = options["quality_profile"]
        self._data["languageProfileId"] = options["language_profile"]
        self._data["seriesType"] = options["series_type"]
        self._data["seasonFolder"] = options["season_folder"]
        self._data["addOptions"] = {
            "searchForMissingEpisodes": options["search"],
            "searchForCutoffUnmetEpisodes": options["unmet_search"],
            "monitor": options["monitor"]
        }
        if "tags" in options:
            self._data["tags"] = options["tags"]
        return self._data

    def add(self,
            root_folder: Union[str, int, RootFolder],
            quality_profile: Union[str, int, QualityProfile],
            language_profile: Union[str, int, LanguageProfile],
            monitor: str = "all",
            season_folder: bool = True,
            search: bool = True,
            unmet_search: bool = True,
            series_type: str = "standard",
            tags: Optional[List[Union[str, int, Tag]]] = None) -> None:
        """ Add this Series to Sonarr.

            Parameters:
                root_folder (Union[str, int, RootFolder]): Root Folder for the Series.
                quality_profile (Union[str, int, QualityProfile]): Quality Profile for the Series.
                language_profile (Union[str, int, LanguageProfile]): Language Profile for the Series.
                monitor (bool): How to monitor the Series. Valid options are all, future, missing, existing, pilot, firstSeason, latestSeason, or none.
                season_folder (bool): Use Season Folders for the Series.
                search (bool): Start search for missing episodes of the Series after adding.
                unmet_search (bool): Start search for cutoff unmet episodes of the Series after adding.
                series_type (str): Series Type for the Series. Valid options are standard, daily, or anime.
                tags (Optional[List[Union[str, int, Tag]]]): Tags to be added to the Series.

            Raises:
                :class:`~arrapi.exceptions.Invalid`: When one of the options given is invalid.
                :class:`~arrapi.exceptions.Exists`: When the Series already Exists in Sonarr.
        """
        options = self._sonarr._validate_add_options(root_folder, quality_profile, language_profile, monitor=monitor,
                                                     season_folder=season_folder, search=search,
                                                     unmet_search=unmet_search, series_type=series_type, tags=tags)
        self._load(load_data=self._sonarr._post_series(self._get_add_data(options)))

    def edit(self,
             path: Optional[str] = None,
             move_files: bool = False,
             quality_profile: Optional[Union[str, int, QualityProfile]] = None,
             language_profile: Optional[Union[str, int, LanguageProfile]] = None,
             monitor: Optional[str] = None,
             monitored: Optional[bool] = None,
             season_folder: Optional[bool] = None,
             series_type: Optional[str] = None,
             tags: Optional[List[Union[str, int, Tag]]] = None,
             apply_tags: str = "add"
             ) -> None:
        """ Edit this Series in Sonarr.

            Parameters:
                path (Optional[str]): Path to change the Series to.
                move_files (bool): When changing the path do you want to move the files to the new path.
                quality_profile (Optional[Union[str, int, QualityProfile]]): Quality Profile to change the Series to.
                language_profile (Optional[Union[str, int, LanguageProfile]]): Language Profile to change the Series to.
                monitor (Optional[str]): How you want the Series monitored. Valid options are all, future, missing, existing, pilot, firstSeason, latestSeason, or none.
                monitored (Optional[bool]): Monitor the Series.
                season_folder (Optional[bool]): Use Season Folders for the Series.
                series_type (Optional[str]): Series Type to change the Series to. Valid options are standard, daily, or anime.
                tags (Optional[List[Union[str, int, Tag]]]): Tags to be added, replaced, or removed from the Series.
                apply_tags (str): How you want to edit the Tags. Valid options are add, replace, or remove.

            Raises:
                :class:`ValueError`: When theres no options given.
                :class:`~arrapi.exceptions.Invalid`: When one of the options given is invalid.
                :class:`~arrapi.exceptions.NotFound`: When the Series isn't found in Sonarr and must be added to Sonarr before editing.
        """
        if not self.id:
            raise NotFound(f"{self.title} not found in Sonarr it must be added before editing")
        options = self._sonarr._validate_edit_options(path=path, move_files=move_files, quality_profile=quality_profile,
                                                      language_profile=language_profile, monitor=monitor,
                                                      monitored=monitored, season_folder=season_folder,
                                                      series_type=series_type, tags=tags, apply_tags=apply_tags)
        if "monitor" in options:
            self._sonarr._edit_series_monitoring([self.id], options.pop("monitor"))
        valid_move_files = options["path"] if "path" in options else False
        for key, value in options.items():
            if key == "tags":
                tag_type = options["apply_tags"]
                if tag_type == "add":
                    self._data[key].extend([t for t in value if t not in self._data["tags"]])
                elif tag_type == "remove":
                    self._data[key] = [t for t in self._data["tags"] if t not in value]
                elif tag_type == "replace":
                    self._data[key] = value
                else:
                    raise Invalid(f"Invalid apply_tags: '{tag_type}' Options: {self._sonarr.apply_tag_options}")
            elif key != ["applyTags", "moveFiles"]:
                self._data[key] = value
        self._load(load_data=self._sonarr._put_series_id(self.id, self._data, moveFiles=valid_move_files))

    def delete(self, addImportExclusion: bool = False, deleteFiles: bool = False) -> None:
        """ Delete this Series from Sonarr.

            Parameters:
                addImportExclusion (bool): Add Import Exclusion for this Series.
                deleteFiles (bool): Delete Files for this Series.

            Raises:
                :class:`~arrapi.exceptions.NotFound`: When the Series isn't found in Sonarr.
        """
        self._sonarr._delete_series_id(self.id, addImportExclusion=addImportExclusion, deleteFiles=deleteFiles)
        self._loading = True
        self.id = None
        self._loading = False


class Season(BaseArr):
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
    def __init__(self, sonarr, data):
        super().__init__(data=data)
        self._sonarr = sonarr
        self.seasonNumber = util.parse(self._data, attribute="seasonNumber", value_type="int")
        self._name = f"Season {self.seasonNumber}"
        self.monitored = util.parse(self._data, attribute="monitored", value_type="bool")
        if "statistics" in data:
            stats = data["statistics"]
            self.totalEpisodeCount = util.parse(stats, attribute="totalEpisodeCount", value_type="int")
            self.episodeCount = util.parse(stats, attribute="episodeCount", value_type="int")
            self.episodeFileCount = util.parse(stats, attribute="episodeFileCount", value_type="int")
            self.sizeOnDisk = util.parse(stats, attribute="sizeOnDisk", value_type="int")
            self.percentOfEpisodes = util.parse(stats, attribute="percentOfEpisodes", value_type="float")
            self.nextAiring = util.parse(data, attribute="nextAiring", value_type="date")
            self.previousAiring = util.parse(data, attribute="previousAiring", value_type="date")
        self._loading = False
