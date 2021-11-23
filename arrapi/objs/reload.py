from abc import abstractmethod
from typing import Union, Optional, List, TYPE_CHECKING

from arrapi import NotFound, Invalid, Exists, Excluded
from arrapi.objs.base import BaseObj

if TYPE_CHECKING:
    from arrapi.objs.simple import RootFolder

class ReloadObj(BaseObj):
    def __init__(self, arr, data, load=False):
        super().__init__(arr, data)
        if load:
            self._load(None)

    @abstractmethod
    def _load(self, data):
        self._partial = data is not None
        super()._load(self._full_load() if data is None else data)

    @abstractmethod
    def _full_load(self):
        pass

    def reload(self):
        """ Reloads the Object """
        self._load(None)


class QualityProfile(ReloadObj):
    """ Represents a single Quality Profile.

        Attributes:
            id (int): ID of the Quality Profile.
            name (str): Name of the Quality Profile.
    """

    def _load(self, data):
        super()._load(data)
        self.id = self._parse(attrs="id", value_type="int")
        self.name = self._parse(attrs="name")
        self._finish(self.name)

    def _full_load(self):
        return self._raw.get_qualityProfileId(self.id)


class LanguageProfile(ReloadObj):
    """ Represents a single Language Profile.

        Attributes:
            id (int): ID of the Language Profile.
            name (str): Name of the Language Profile.
    """

    def _load(self, data):
        super()._load(data)
        self.id = self._parse(attrs="id", value_type="int")
        self.name = self._parse(attrs="name")
        self._finish(self.name)

    def _full_load(self):
        return self._raw.get_languageProfileId(self.id)

class SystemStatus(ReloadObj):
    """ Represents the System Status.

        Attributes:
            version (str): Version of the Arr Instance.

        Check dir(SystemStatus) for all attribute as the rest are auto built.
    """

    def __init__(self, arr):
        super().__init__(arr, None)

    def _load(self, data):
        super()._load(None)
        self.version = ""
        for key, value in self._data.items():
            if key.startswith("is") or key == "migrationVersion":
                setattr(self, key, self._parse(data=value, value_type="int"))
            elif key.endswith("Time"):
                setattr(self, key, self._parse(data=value, value_type="date"))
            elif key == "version":
                self.version = value
            else:
                setattr(self, key, value)
        self._finish(self.version)

    def _full_load(self):
        return self._raw.get_system_status()


class Tag(ReloadObj):
    """ Represents a single Tag.

        Attributes:
            id (int): ID of the Tag.
            label (str): Label of the Tag.
            detail (bool): If the Tag was loaded with details.
            delayProfileIds (List[int]): Delay Profile IDs. (Only when loaded with details)
            notificationIds (List[int]): Notification IDs. (Only when loaded with details)
            restrictionIds (List[int]): Restriction IDs. (Only when loaded with details)
            importListIds (List[int]): Import List IDs. (Only when loaded with details)
            movieIds (List[int]): Radarr Movie IDs. (Only when loaded with details using :class:`~arrapi.apis.radarr.RadarrAPI`)
            seriesIds (List[int]): Sonarr Series IDs. (Only when loaded with details using :class:`~arrapi.apis.radarr.SonarrAPI`)
            artistIds (List[int]): Lidarr Artist IDs. (Only when loaded with details using :class:`~arrapi.apis.lidarr.LidarrAPI`)
            authorIds (List[int]): Readarr Author IDs. (Only when loaded with details using :class:`~arrapi.apis.readarr.ReadarrAPI`)
    """

    def _load(self, data):
        super()._load(data)
        self.label = self._parse(attrs="label")
        self.id = self._parse(attrs="id", value_type="int", default_is_none=True)
        self.detail = False
        if "delayProfileIds" in self._data:
            self.detail = True
            self.delayProfileIds = self._parse(attrs="delayProfileIds", value_type="int", is_list=True)
            self.notificationIds = self._parse(attrs="notificationIds", value_type="int", is_list=True)
            self.restrictionIds = self._parse(attrs="restrictionIds", value_type="int", is_list=True)
            self.importListIds = self._parse(attrs="importListIds", value_type="int", is_list=True)
        if "movieIds" in self._data:
            self.movieIds = self._parse(attrs="movieIds", value_type="int", is_list=True)
        if "seriesIds" in self._data:
            self.seriesIds = self._parse(attrs="seriesIds", value_type="int", is_list=True)
        if "artistIds" in self._data:
            self.artistIds = self._parse(attrs="artistIds", value_type="int", is_list=True)
        if "authorIds" in self._data:
            self.authorIds = self._parse(attrs="authorIds", value_type="int", is_list=True)
        self._finish(self.label)

    def __str__(self):
        return f"[{self.id}:{self._name}]" if self.id and self._name else f"[Tag:{self.id}]"

    def _full_load(self):
        return self._raw.get_tag_id(self.id, detail=self.detail)

    def edit(self, label: str) -> None:
        """ Edit the :class:`~arrapi.objs.reload.Tag`.

            Parameters:
                label (str): Label to change tag to.

        """
        self._load(self._raw.put_tag_id(self.id, label))

    def delete(self) -> None:
        """ Delete the :class:`~arrapi.objs.reload.Tag`."""
        self._raw.delete_tag_id(self.id)


class Movie(ReloadObj):
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
            tags (List[:class:`~arrapi.objs.reload.Tag`]): List of tags for the Movie.
            tagsIds (List[int]): List of tag ids for the Movie.
            rating_votes (int): Number of votes for the Movie.
            rating_value (float): Rating of the Movie.
            originalTitle (str): Original Title of the Movie. (Radarr v3 Only)
            digitalRelease (datetime): Date the Movie was Released Digitally. (Radarr v3 Only)
            qualityProfileId (int): Quality Profile ID of the Movie. (Radarr v3 Only)
            qualityProfile (:class:`~arrapi.objs.reload.QualityProfile`): Quality Profile of the Movie. (Radarr v3 Only)
            collection_name (str): Collection Name of the Movie. (Radarr v3 Only)
            collection_tmdbId (int): TMDb Collection ID for the Movie. (Radarr v3 Only)
            downloaded (bool): If the Movie has been Downloaded. (Radarr v2 Only)
            profileId (int): Quality Profile ID of the Movie. (Radarr v2 Only)
            profile (:class:`~arrapi.objs.reload.QualityProfile`): Quality Profile of the Movie. (Radarr v2 Only)
    """

    def __init__(self, radarr, data=None, movie_id=None, tmdb_id=None, imdb_id=None):
        self._loading = True
        self.id = movie_id
        self.tmdbId = tmdb_id
        self.imdbId = imdb_id
        super().__init__(radarr, data)

    def _load(self, data):
        super()._load(data)
        self.title = self._parse(attrs="title")
        self.sortTitle = self._parse(attrs="sortTitle")
        self.sizeOnDisk = self._parse(attrs="sizeOnDisk", value_type="int")
        self.status = self._parse(attrs="status")
        self.overview = self._parse(attrs="overview")
        self.inCinemas = self._parse(attrs="inCinemas", value_type="date")
        self.physicalRelease = self._parse(attrs="physicalRelease", value_type="date")
        self.website = self._parse(attrs="website")
        self.year = self._parse(attrs="year", value_type="int")
        self.hasFile = self._parse(attrs="hasFile", value_type="bool")
        self.youTubeTrailerId = self._parse(attrs="youTubeTrailerId")
        self.studio = self._parse(attrs="studio")
        self.path = self._parse(attrs="path")
        self.monitored = self._parse(attrs="monitored", value_type="bool")
        self.minimumAvailability = self._parse(attrs="minimumAvailability")
        self.isAvailable = self._parse(attrs="isAvailable", value_type="bool")
        self.folderName = self._parse(attrs="folderName")
        self.runtime = self._parse(attrs="runtime", value_type="int")
        self.cleanTitle = self._parse(attrs="cleanTitle")
        self.imdbId = self._parse(attrs="imdbId")
        self.tmdbId = self._parse(attrs="tmdbId", value_type="int", default_is_none=True)
        self.titleSlug = self._parse(attrs="titleSlug")
        self.certification = self._parse(attrs="certification")
        self.genres = self._parse(attrs="genres", is_list=True)
        self.tagsIds = self._parse(attrs="tags", value_type="int", is_list=True)
        self.tags = self._parse(attrs="tags", value_type="intTag", is_list=True)
        self.rating_votes = self._parse(attrs=["rating", "votes"], value_type="int")
        self.rating_value = self._parse(attrs=["rating", "value"], value_type="float")
        self.id = self._parse(attrs="id", value_type="int", default_is_none=True)
        if self._raw.v3:
            self.originalTitle = self._parse(attrs="originalTitle")
            self.digitalRelease = self._parse(attrs="digitalRelease", value_type="date")
            self.qualityProfileId = self._parse(attrs="qualityProfileId", value_type="int")
            self.qualityProfile = self._parse(attrs="qualityProfileId", value_type="intQualityProfile")
            self.collection_name = self._parse(attrs=["collection", "name"])
            self.collection_tmdbId = self._parse(attrs=["collection", "tmdbId"], value_type="int", default_is_none=True)
        else:
            self.downloaded = self._parse(attrs="downloaded", value_type="bool")
            self.profileId = self._parse(attrs="profileId", value_type="int")
            self.profile = self._parse(attrs="profileId", value_type="intQualityProfile")
        self._finish(self.title)

    def _full_load(self):
        if self.id:
            return self._raw.get_movie_id(self.id)
        elif self.tmdbId or self.imdbId:
            items = self._raw.get_movie_lookup(f"tmdb:{self.tmdbId}" if self.tmdbId else f"imdb:{self.imdbId}")
            if items:
                return items[0]
            else:
                raise NotFound("Item Not Found")
        else:
            raise Invalid("Load Failed: No Load Input")

    def _get_add_data(self, options, path=None):
        if self.id:
            raise Exists(f"{self.title} is already in Radarr")
        self._data.pop("Id", None)
        self._data["monitored"] = options["monitor"]
        if path:
            if not path.startswith(options["root_folder"]):
                raise Invalid(f"Individual Path: {path} must start with the Root Folder: {options['root_folder']} ")
            self._data["path"] = path
        else:
            self._data["rootFolderPath"] = options["root_folder"]
        self._data["rootFolderPath"] = options["root_folder"]
        self._data["qualityProfileId" if self._raw.v3 else "profileId"] = options["quality_profile"]
        self._data["minimumAvailability"] = options["minimum_availability"]
        self._data["addOptions"] = {"searchForMovie": options["search"]}
        if "tags" in options:
            self._data["tags"] = options["tags"]
        return self._data

    def add(self,
            root_folder: Union[str, int, "RootFolder"],
            quality_profile: Union[str, int, "QualityProfile"],
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
        if self._arr.exclusions and self.tmdbId in self._arr.exclusions:
            raise Excluded(f"TMDb ID: {self.tmdbId} is excluded from being added.")
        self._load(self._raw.post_movie(self._get_add_data(self._arr._validate_add_options(
            root_folder,
            quality_profile,
            monitor=monitor,
            search=search,
            minimum_availability=minimum_availability,
            tags=tags
        ))))

    def edit(self,
             path: Optional[str] = None,
             move_files: bool = False,
             quality_profile: Optional[Union[str, int, "QualityProfile"]] = None,
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
                :class:`~arrapi.exceptions.NotFound`: When the Movie hasn't been added to Radarr.
        """
        if not self.id:
            raise NotFound(f"{self.title} not found Radarr, it must be added before editing")
        options = self._arr._validate_edit_options(path=path, move_files=move_files, quality_profile=quality_profile,
                                                   monitored=monitored, minimum_availability=minimum_availability,
                                                   tags=tags, apply_tags=apply_tags)
        valid_move_files = options["path"] if "path" in options else False
        for key, value in options.items():
            if key == "tags":
                tag_type = options["applyTags"]
                if tag_type == "add":
                    self._data[key].extend([t for t in value if t not in self._data["tags"]])
                elif tag_type == "remove":
                    self._data[key] = [t for t in self._data["tags"] if t not in value]
                elif tag_type == "replace":
                    self._data[key] = value
                else:
                    raise Invalid(f"Invalid apply_tags: '{tag_type}' Options: {self._arr.apply_tags_options}")
            elif key != ["applyTags", "moveFiles"]:
                self._data[key] = value
        self._load(self._raw.put_movie_id(self.id, self._data, moveFiles=valid_move_files))

    def delete(self, addImportExclusion: bool = False, deleteFiles: bool = False) -> None:
        """ Delete this Movie from Radarr.

            Parameters:
                addImportExclusion (bool): Add Import Exclusion for this Movie.
                deleteFiles (bool): Delete Files for this Movie.

            Raises:
                :class:`~arrapi.exceptions.NotFound`: When the Movie hasn't been added to Radarr.
        """
        if not self.id:
            raise NotFound(f"{self.title} not found Radarr, it must be added before deleting")
        self._raw.delete_movie_id(self.id, addImportExclusion=addImportExclusion, deleteFiles=deleteFiles)
        self._loading = True
        self.id = None
        self._loading = False


class Series(ReloadObj):
    """ Represents a single Series.

        Attributes:
            id (int): ID of the Series.
            title (str): Title of the Series.
            sortTitle (str): Sort Title of the Series.
            status (str): Status of the Series.
            overview (str): Overview of the Series.
            seasons (List[:class:`~arrapi.objs.simple.Season`]): List of Seasons in the Series.
            nextAiring (datetime): Date the next Episode in the Series Airs.
            previousAiring (datetime): Date the latest Episode in the Series Aired.
            network (str): Network the Series Airs on.
            airTime (str): Time Series Airs.
            year (int): Year of the Series.
            path (str): Path of the Series.
            languageProfileId (int): Language Profile ID of the Series.
            languageProfile (:class:`~arrapi.objs.reload.LanguageProfile`)): Language Profile of the Series.
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
            tags (List[:class:`~arrapi.objs.reload.Tag`]): List of tags for the Movie.
            tagsIds (List[int]): List of tag ids for the Movie.
            rating_votes (int): Number of votes for the Series.
            rating_value (float): Rating of the Series.
            seasonCount (int): Number of Seasons in the Series.
            totalEpisodeCount (int): Total Episodes in the Series.
            episodeCount (int): Episodes in the Series.
            episodeFileCount (int): Episode File Count for the Series.
            sizeOnDisk (int): Size on Disk for the Series.
            ended (bool): If the Series has ended. (Sonarr v3 Only)
            rootFolderPath (str): Root Folder Path for the Series. (Sonarr v3 Only)
            qualityProfileId (int): Quality Profile ID of the Series. (Sonarr v3 Only)
            qualityProfile (:class:`~arrapi.objs.reload.QualityProfile`): Quality Profile of the Series. (Sonarr v3 Only)
            percentOfEpisodes (float): Percent of Episodes obtained. (Sonarr v3 Only)
            profileId (int): Quality Profile ID of the Series. (Sonarr v2 Only)
            profile (:class:`~arrapi.objs.reload.QualityProfile`): Quality Profile of the Series. (Sonarr v2 Only)
    """

    def __init__(self, sonarr, data=None, series_id=None, tvdb_id=None):
        self._loading = True
        self.id = series_id
        self.tvdbId = tvdb_id
        super().__init__(sonarr, data, load=series_id or tvdb_id)

    def _load(self, data):
        super()._load(data)
        self.title = self._parse(attrs="title")
        self.sortTitle = self._parse(attrs="sortTitle")
        self.status = self._parse(attrs="status")
        self.overview = self._parse(attrs="overview")
        self.nextAiring = self._parse(attrs="nextAiring", value_type="date")
        self.previousAiring = self._parse(attrs="previousAiring", value_type="date")
        self.network = self._parse(attrs="network")
        self.airTime = self._parse(attrs="airTime")
        self.year = self._parse(attrs="year", value_type="int")
        self.path = self._parse(attrs="path")
        self.languageProfileId = self._parse(attrs="languageProfileId", value_type="int")
        self.languageProfile = self._parse(attrs="languageProfileId", value_type="intLanguageProfile")
        self.seasonFolder = self._parse(attrs="seasonFolder", value_type="bool")
        self.monitored = self._parse(attrs="monitored", value_type="bool")
        self.useSceneNumbering = self._parse(attrs="useSceneNumbering", value_type="bool")
        self.runtime = self._parse(attrs="runtime", value_type="int")
        self.cleanTitle = self._parse(attrs="cleanTitle")
        self.imdbId = self._parse(attrs="imdbId")
        self.tvdbId = self._parse(attrs="tvdbId", value_type="int")
        self.tvRageId = self._parse(attrs="tvRageId", value_type="int")
        self.tvMazeId = self._parse(attrs="tvMazeId", value_type="int")
        self.titleSlug = self._parse(attrs="titleSlug")
        self.firstAired = self._parse(attrs="firstAired", value_type="date")
        self.seriesType = self._parse(attrs="seriesType")
        self.certification = self._parse(attrs="certification")
        self.genres = self._parse(attrs="genres", is_list=True)
        self.tagsIds = self._parse(attrs="tags", value_type="int", is_list=True)
        self.tags = self._parse(attrs="tags", value_type="intTag", is_list=True)
        if "rating" in self._data:
            self.rating_votes = self._parse(attrs=["rating", "votes"], value_type="int")
            self.rating_value = self._parse(attrs=["rating", "value"], value_type="float")
        self.id = self._parse(attrs="id", value_type="int", default_is_none=True)
        self.seasons = self._parse(attrs="seasons", value_type="season", is_list=True)

        if self._raw.v3:
            self.ended = self._parse(attrs="ended", value_type="bool")
            self.rootFolderPath = self._parse(attrs="rootFolderPath")
            self.qualityProfileId = self._parse(attrs="qualityProfileId", value_type="int")
            self.qualityProfile = self._parse(attrs="qualityProfileId", value_type="intQualityProfile")
            if "statistics" in self._data:
                self.seasonCount = self._parse(attrs=["statistics", "seasonCount"], value_type="int")
                self.totalEpisodeCount = self._parse(attrs=["statistics", "totalEpisodeCount"], value_type="int")
                self.episodeCount = self._parse(attrs=["statistics", "episodeCount"], value_type="int")
                self.episodeFileCount = self._parse(attrs=["statistics", "episodeFileCount"], value_type="int")
                self.sizeOnDisk = self._parse(attrs=["statistics", "sizeOnDisk"], value_type="int")
                self.percentOfEpisodes = self._parse(attrs=["statistics", "percentOfEpisodes"], value_type="float")
        else:
            self.profileId = self._parse(attrs="profileId", value_type="int")
            self.profile = self._parse(attrs="profileId", value_type="intQualityProfile")
            self.seasonCount = self._parse(attrs="seasonCount", value_type="int")
            self.totalEpisodeCount = self._parse(attrs="totalEpisodeCount", value_type="int")
            self.episodeCount = self._parse(attrs="episodeCount", value_type="int")
            self.episodeFileCount = self._parse(attrs="episodeFileCount", value_type="int")
            self.sizeOnDisk = self._parse(attrs="sizeOnDisk", value_type="int")
        self._finish(self.title)

    def _full_load(self):
        if self.id:
            return self._raw.get_series_id(self.id)
        elif self.tvdbId:
            items = self._raw.get_series_lookup(f"tvdb:{self.tvdbId}")
            if items:
                return items[0]
            else:
                raise NotFound("Item Not Found")
        else:
            raise Invalid("Load Failed: No Load Input")

    def _get_add_data(self, options, path=None):
        if self.id:
            raise Exists(f"{self.title} is already in Sonarr")
        self._data.pop("Id", None)
        self._data["rootFolderPath"] = options["root_folder"]
        if path:
            if not path.startswith(options["root_folder"]):
                raise Invalid(f"Individual Path: {path} must start with the Root Folder: {options['root_folder']} ")
            self._data["path"] = path
        else:
            self._data["rootFolderPath"] = options["root_folder"]
        self._data["monitored"] = options["monitored"]
        self._data["qualityProfileId" if self._raw.v3 else "profileId"] = options["quality_profile"]
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
            root_folder: Union[str, int, "RootFolder"],
            quality_profile: Union[str, int, "QualityProfile"],
            language_profile: Union[str, int, "LanguageProfile"],
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
        if self._arr.exclusions and self.tvdbId in self._arr.exclusions:
            raise Excluded(f"TVDb ID: {self.tvdbId} is excluded from being added.")
        self._load(self._raw.post_series(self._get_add_data(self._arr._validate_add_options(
            root_folder,
            quality_profile,
            language_profile,
            monitor=monitor,
            season_folder=season_folder,
            search=search,
            unmet_search=unmet_search,
            series_type=series_type,
            tags=tags
        ))))

    def edit(self,
             path: Optional[str] = None,
             move_files: bool = False,
             quality_profile: Optional[Union[str, int, "QualityProfile"]] = None,
             language_profile: Optional[Union[str, int, "LanguageProfile"]] = None,
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
                :class:`~arrapi.exceptions.NotFound`: When the Series hasn't been added to Sonarr.
        """
        if not self.id:
            raise NotFound(f"{self.title} not found in Sonarr, it must be added before editing")
        options = self._arr._validate_edit_options(path=path, move_files=move_files, quality_profile=quality_profile,
                                                   language_profile=language_profile, monitor=monitor,
                                                   monitored=monitored, season_folder=season_folder,
                                                   series_type=series_type, tags=tags, apply_tags=apply_tags)
        if "monitor" in options:
            self._raw.edit_series_monitoring([self.id], options.pop("monitor"))
        valid_move_files = options["path"] if "path" in options else False
        for key, value in options.items():
            if key == "tags":
                tag_type = options["applyTags"]
                if tag_type == "add":
                    self._data[key].extend([t for t in value if t not in self._data["tags"]])
                elif tag_type == "remove":
                    self._data[key] = [t for t in self._data["tags"] if t not in value]
                elif tag_type == "replace":
                    self._data[key] = value
                else:
                    raise Invalid(f"Invalid apply_tags: '{tag_type}' Options: {self._arr.apply_tags_options}")
            elif key != ["applyTags", "moveFiles"]:
                self._data[key] = value
        self._load(self._raw.put_series_id(self.id, self._data, moveFiles=valid_move_files))

    def delete(self, addImportExclusion: bool = False, deleteFiles: bool = False) -> None:
        """ Delete this Series from Sonarr.

            Parameters:
                addImportExclusion (bool): Add Import Exclusion for this Series.
                deleteFiles (bool): Delete Files for this Series.

            Raises:
                :class:`~arrapi.exceptions.NotFound`: When the Series hasn't been added to Sonarr.
        """
        if not self.id:
            raise NotFound(f"{self.title} not found in Sonarr, it must be added before deleting")
        self._raw.delete_series_id(self.id, addImportExclusion=addImportExclusion, deleteFiles=deleteFiles)
        self._loading = True
        self.id = None
        self._loading = False
