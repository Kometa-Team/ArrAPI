from requests import Session
from typing import Optional, Union, List, Tuple
from arrapi import LanguageProfile, RootFolder, QualityProfile, Series, Tag, NotFound, Invalid, Exists
from .base import BaseAPI
from ..objs.simple import SonarrExclusion
from ..raws.sonarr import SonarrRawAPI


class SonarrAPI(BaseAPI):
    """ Primary Class to use when connecting with the Sonarr API

        Parameters:
            url (str): URL of Sonarr application.
            apikey (str): apikey for the Sonarr application.
            session (Optional[Session]): Session object to use.
     """

    def __init__(self, url: str, apikey: str, session: Optional[Session] = None) -> None:
        super().__init__(SonarrRawAPI(url, apikey, session=session))
        self.exclusions = []
        self.monitor_options = ["all", "future", "missing", "existing", "pilot", "firstSeason", "latestSeason", "none"]
        self.series_type_options = ["standard", "daily", "anime"]

    def _validate_add_options(self, root_folder, quality_profile, language_profile, monitor="all",
                              season_folder=True, search=True, unmet_search=False, series_type="standard",
                              tags=None):
        """ Validate Add Series options. """
        options = {
            "root_folder": self._validate_root_folder(root_folder),
            "quality_profile" if self._raw.v3 else "profileId": self._validate_quality_profile(quality_profile),
            "language_profile": self._validate_language_profile(language_profile),
            "monitor": self._validate_monitor(monitor),
            "monitored": monitor != "none",
            "season_folder": True if season_folder else False,
            "search": True if search else False,
            "unmet_search": True if unmet_search else False,
            "series_type": self._validate_series_type(series_type),
        }
        if tags:
            options["tags"] = self._validate_tags(tags)
        return options

    def _validate_edit_options(self, root_folder=None, path=None, move_files=False, quality_profile=None,
                               language_profile=None, monitor=None, monitored=None, season_folder=None,
                               series_type=None, tags=None, apply_tags="add"):
        """ Validate Edit Series options. """
        variables = [root_folder, path, quality_profile, language_profile, monitor,
                     monitored, season_folder, series_type, tags]
        if all(v is None for v in variables):
            raise ValueError("Expected either root_folder, path, quality_profile, language_profile, "
                             "monitor, monitored, season_folder, series_type, or tags args")
        options = {"moveFiles": True if move_files else False}
        if root_folder is not None:
            options["rootFolderPath"] = self._validate_root_folder(root_folder)
        if path is not None:
            options["path"] = path
        if quality_profile is not None:
            options["qualityProfileId" if self._raw.v3 else "profileId"] = self._validate_quality_profile(quality_profile)
        if language_profile is not None:
            options["languageProfileId"] = self._validate_language_profile(language_profile)
        if monitor is not None:
            options["monitor"] = self._validate_monitor(monitor)
        if monitored is not None:
            options["monitored"] = True if monitored else False
        if season_folder is not None:
            options["seasonFolder"] = True if season_folder else False
        if series_type is not None:
            options["seriesType"] = self._validate_series_type(series_type)
        if tags is not None:
            options["tags"] = self._validate_tags(tags, create=apply_tags != "remove")
            if apply_tags in self.apply_tags_options:
                options["applyTags"] = apply_tags
            else:
                raise Invalid(f"Invalid apply_tags: '{apply_tags}' Options: {self.apply_tags_options}")
        return options

    def _validate_monitor(self, monitor):
        """ Validate Monitor options. """
        return self._validate_options("Monitor", monitor, self.monitor_options)

    def _validate_series_type(self, series_type):
        """ Validate Series Type options. """
        return self._validate_options("Series Type", series_type, self.series_type_options)

    def _validate_tvdb_ids(self, tvdb_ids):
        """ Validate TVDb IDs. """
        valid_ids = []
        invalid_ids = []
        tvdb_sonarr_ids = {m.tvdbId: m for m in self.all_series()}
        for tvdb_id in tvdb_ids:
            if isinstance(tvdb_id, Series):
                tvdb_id = tvdb_id.tvdbId
            if tvdb_id in tvdb_sonarr_ids:
                valid_ids.append(tvdb_sonarr_ids[tvdb_id].id)
            else:
                invalid_ids.append(tvdb_id)
        return valid_ids, invalid_ids

    def respect_list_exclusions_when_adding(self):
        """ Stores all List Exclusions so whenever :func:`~arrapi.objs.reload.Series.add` or :func:`~arrapi.apis.sonarr.SonarrAPI.add_multiple_series` is called the additions will be checked against the Exclusion List  """
        self.exclusions = [SonarrExclusion(self, ex).tvdbId for ex in self._raw.get_importlistexclusion()]

    def get_series(self, series_id: Optional[int] = None, tvdb_id: Optional[int] = None) -> Series:
        """ Gets a :class:`~arrapi.objs.reload.Series` by one of the IDs.

            Parameters:
                series_id (Optional[int]): Search by Sonarr Series ID.
                tvdb_id (Optional[int]): Search by TVDb ID.

            Returns:
                :class:`~arrapi.objs.reload.Series`: Series for the ID given.

            Raises:
                :class:`ValueError`: When no ID is given.
                :class:`~arrapi.exceptions.NotFound`: When there's no series with that ID.
        """
        if all(v is None for v in [series_id, tvdb_id]):
            raise ValueError("Expected either series_id or tvdb_id args")
        return Series(self, series_id=series_id, tvdb_id=tvdb_id)

    def all_series(self) -> List[Series]:
        """ Gets all :class:`~arrapi.objs.reload.Series` in Sonarr.

            Returns:
                List[:class:`~arrapi.objs.reload.Series`]: List of Series in Sonarr.
        """
        return [Series(self, data=d) for d in self._raw.get_series()]

    def search_series(self, term: str) -> List[Series]:
        """ Gets a list of :class:`~arrapi.objs.reload.Series` by a search term.

            Parameters:
                term (str): Term to Search for.

            Returns:
                List[:class:`~arrapi.objs.reload.Series`]: List of Series's found.
        """
        return [Series(self, data=d) for d in self._raw.get_series_lookup(term)]

    def add_series(
            self,
            root_folder: Union[str, int, "RootFolder"],
            quality_profile: Union[str, int, "QualityProfile"],
            language_profile: Union[str, int, "LanguageProfile"],
            series_id: Optional[int] = None,
            tvdb_id: Optional[int] = None,
            monitor: str = "all",
            season_folder: bool = True,
            search: bool = True,
            unmet_search: bool = True,
            series_type: str = "standard",
            tags: Optional[List[Union[str, int, Tag]]] = None
    ) -> Series:
        """ Gets a :class:`~arrapi.objs.reload.Series` by one of the IDs and adds it to Sonarr.

            Parameters:
                root_folder (Union[str, int, RootFolder]): Root Folder for the Series.
                quality_profile (Union[str, int, QualityProfile]): Quality Profile for the Series.
                language_profile (Union[str, int, LanguageProfile]): Language Profile for the Series.
                series_id (Optional[int]): Search by Sonarr Series ID.
                tvdb_id (Optional[int]): Search by TVDb ID.
                monitor (bool): How to monitor the Series. Valid options are all, future, missing, existing, pilot, firstSeason, latestSeason, or none.
                season_folder (bool): Use Season Folders for the Series.
                search (bool): Start search for missing episodes of the Series after adding.
                unmet_search (bool): Start search for cutoff unmet episodes of the Series after adding.
                series_type (str): Series Type for the Series. Valid options are standard, daily, or anime.
                tags (Optional[List[Union[str, int, Tag]]]): Tags to be added to the Series.

            Returns:
                :class:`~arrapi.objs.reload.Series`: Series for the ID given.

            Raises:
                :class:`ValueError`: When no ID is given.
                :class:`~arrapi.exceptions.NotFound`: When there's no series with that ID.
                :class:`~arrapi.exceptions.Invalid`: When one of the options given is invalid.
                :class:`~arrapi.exceptions.Exists`: When the Series already Exists in Sonarr.
        """
        series = self.get_series(series_id=series_id, tvdb_id=tvdb_id)
        series.add(root_folder, quality_profile, language_profile, monitor=monitor, season_folder=season_folder,
                   search=search, unmet_search=unmet_search, series_type=series_type, tags=tags)
        return series

    def edit_series(
            self,
            series_id: Optional[int] = None,
            tvdb_id: Optional[int] = None,
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
            ) -> Series:
        """ Gets a :class:`~arrapi.objs.reload.Series` by one of the IDs and edits it in Sonarr.

            Parameters:
                series_id (Optional[int]): Search by Sonarr Series ID.
                tvdb_id (Optional[int]): Search by TVDb ID.
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

            Returns:
                :class:`~arrapi.objs.reload.Series`: Series for the ID given.

            Raises:
                :class:`ValueError`: When no ID is given or when theres no options given.
                :class:`~arrapi.exceptions.Invalid`: When one of the options given is invalid.
                :class:`~arrapi.exceptions.NotFound`: When there's no series with that ID or when the Series hasn't been added to Sonarr.
        """
        series = self.get_series(series_id=series_id, tvdb_id=tvdb_id)
        series.edit(path=path, move_files=move_files, quality_profile=quality_profile,
                    language_profile=language_profile, monitor=monitor, monitored=monitored,
                    season_folder=season_folder, series_type=series_type, tags=tags, apply_tags=apply_tags)
        return series

    def delete_series(
            self,
            series_id: Optional[int] = None,
            tvdb_id: Optional[int] = None,
            addImportExclusion: bool = False,
            deleteFiles: bool = False
    ) -> Series:
        """ Gets a :class:`~arrapi.objs.reload.Series` by one of the IDs and deletes it from Sonarr.

            Parameters:
                series_id (Optional[int]): Search by Sonarr Series ID.
                tvdb_id (Optional[int]): Search by TVDb ID.
                addImportExclusion (bool): Add Import Exclusion for this Series.
                deleteFiles (bool): Delete Files for this Series.

            Returns:
                :class:`~arrapi.objs.reload.Series`: Series for the ID given.

            Raises:
                :class:`ValueError`: When no ID is given.
                :class:`~arrapi.exceptions.NotFound`: When there's no series with that ID or when the Series hasn't been added to Sonarr.
        """
        series = self.get_series(series_id=series_id, tvdb_id=tvdb_id)
        series.delete(addImportExclusion=addImportExclusion, deleteFiles=deleteFiles)
        return series

    def add_multiple_series(self, ids: List[Union[Series, int, Tuple[Union[Series, int], str]]],
                            root_folder: Union[str, int, RootFolder],
                            quality_profile: Union[str, int, QualityProfile],
                            language_profile: Union[str, int, LanguageProfile],
                            monitor: str = "all",
                            season_folder: bool = True,
                            search: bool = True,
                            unmet_search: bool = True,
                            series_type: str = "standard",
                            tags: Optional[List[Union[str, int, Tag]]] = None,
                            per_request: int = None
                            ) -> Tuple[List[Series], List[Series], List[Union[int, Series]]]:
        """ Adds multiple Series to Sonarr in a single call by their TVDb IDs.

            You can specify the path for each TVDb ID using a tuple in the list instead of just the ID ex. ``(121361, "/media/Game of Thrones/")``

            The path provided must begin with the root_folder specified.

            Parameters:
                ids (List[Union[Series, int, Tuple[Union[Series, int], str]]]): List of TVDB IDs or Series lookups to add.
                root_folder (Union[str, int, RootFolder]): Root Folder for the Series.
                quality_profile (Union[str, int, QualityProfile]): Quality Profile for the Series.
                language_profile (Union[str, int, LanguageProfile]): Language Profile for the Series.
                monitor (bool): How to monitor the Series. Valid options are ``all``, ``future``, ``missing``, ``existing``, ``pilot``, ``firstSeason``, ``latestSeason``, or ``none``.
                season_folder (bool): Use Season Folders for the Series.
                search (bool): Start search for missing episodes of the Series after adding.
                unmet_search (bool): Start search for cutoff unmet episodes of the Series after adding.
                series_type (str): Series Type for the Series. Valid options are ``standard``, ``daily``, or ``anime``.
                tags (Optional[List[Union[str, int, Tag]]]): Tags to be added to the Series.
                per_request (int): Number of Series to add per request.

            Returns:
                Tuple[List[:class:`~arrapi.objs.reload.Series`], List[:class:`~arrapi.objs.reload.Series`], List[Union[int, Series]]]: List of Series that were able to be added, List of Series already in Sonarr, List of Series that could not be found or were excluded.

            Raises:
                :class:`~arrapi.exceptions.Invalid`: When one of the options given is invalid.
        """
        options = self._validate_add_options(root_folder, quality_profile, language_profile, monitor=monitor,
                                             season_folder=season_folder, search=search, unmet_search=unmet_search,
                                             series_type=series_type, tags=tags)
        json = []
        series = []
        existing_series = []
        invalid_ids = []
        for item in ids:
            path = item[1] if isinstance(item, tuple) else None
            item = item[0] if isinstance(item, tuple) else item
            try:
                if isinstance(item, Series):
                    show = item
                else:
                    if self.exclusions and int(item) in self.exclusions:
                        raise NotFound
                    show = self.get_series(tvdb_id=item)
                if self.exclusions and show.tvdbId in self.exclusions:
                    raise NotFound
                try:
                    json.append(show._get_add_data(options, path=path))
                except Exists:
                    existing_series.append(show)
            except NotFound:
                invalid_ids.append(item)
        if len(json) > 0:
            if per_request is None:
                per_request = len(json)
            for i in range(0, len(json), per_request):
                series.extend([Series(self, data=s) for s in self._raw.post_series_import(json[i:i+per_request])])
        return series, existing_series, invalid_ids

    def edit_multiple_series(self, ids: List[Union[Series, int]],
                             root_folder: Optional[Union[str, int, RootFolder]] = None,
                             move_files: bool = False,
                             quality_profile: Optional[Union[str, int, QualityProfile]] = None,
                             language_profile: Optional[Union[str, int, LanguageProfile]] = None,
                             monitor: Optional[str] = None,
                             monitored: Optional[bool] = None,
                             season_folder: Optional[bool] = None,
                             series_type: Optional[str] = None,
                             tags: Optional[List[Union[str, int, Tag]]] = None,
                             apply_tags: str = "add",
                             per_request: int = None
                             ) -> Tuple[List[Series], List[Union[Series, int]]]:
        """ Edit multiple Series in Sonarr by their TVDb IDs.

            Parameters:
                ids (List[Union[int, Series]]): List of Series IDs or Series objects you want to edit.
                root_folder (Union[str, int, RootFolder]): Root Folder to change the Series to.
                move_files (bool): When changing the root folder do you want to move the files to the new path.
                quality_profile (Optional[Union[str, int, QualityProfile]]): Quality Profile to change the Series to.
                language_profile (Optional[Union[str, int, LanguageProfile]]): Language Profile to change the Series to.
                monitor (Optional[str]): How you want the Series monitored. Valid options are all, future, missing, existing, pilot, firstSeason, latestSeason, or none.
                monitored (Optional[bool]): Monitor the Series.
                season_folder (Optional[bool]): Use Season Folders for the Series.
                series_type (Optional[str]): Series Type to change the Series to. Valid options are standard, daily, or anime.
                tags (Optional[List[Union[str, int, Tag]]]): Tags to be added, replaced, or removed from the Series.
                apply_tags (str): How you want to edit the Tags. Valid options are add, replace, or remove.
                per_request (int): Number of Series to edit per request.

            Returns:
                Tuple[List[:class:`~arrapi.objs.reload.Series`], List[Union[Series, int]]]: List of Series that were able to be edited, List of Series that could not be found in Sonarr.

            Raises:
                :class:`~arrapi.exceptions.Invalid`: When one of the options given is invalid.
        """
        json = self._validate_edit_options(root_folder=root_folder, move_files=move_files,
                                           quality_profile=quality_profile, language_profile=language_profile,
                                           monitor=monitor, monitored=monitored, season_folder=season_folder,
                                           series_type=series_type, tags=tags, apply_tags=apply_tags)
        series_list = []
        valid_ids, invalid_ids = self._validate_tvdb_ids(ids)
        if len(valid_ids) > 0:
            if per_request is None:
                per_request = len(valid_ids)
            if "monitor" in json:
                json_monitor = json.pop("monitor")
                for i in range(0, len(valid_ids), per_request):
                    self._raw.edit_series_monitoring(valid_ids[i:i+per_request], json_monitor)
            for i in range(0, len(valid_ids), per_request):
                json["seriesIds"] = valid_ids[i:i+per_request]
                series_list.extend([Series(self, data=s) for s in self._raw.put_series_editor(json)])
        return series_list, invalid_ids

    def delete_multiple_series(self, ids: List[Union[int, Series]],
                               addImportExclusion: bool = False,
                               deleteFiles: bool = False,
                               per_request: int = None
                               ) -> List[Union[Series, int]]:
        """ Deletes multiple Series in Sonarr by their TVDb IDs.

            Parameters:
                ids (List[Union[int, Series]]): List of TVDb IDs or Series objects you want to delete.
                addImportExclusion (bool): Add Import Exclusion for these TVDb IDs.
                deleteFiles (bool): Delete Files for these TVDb IDs.
                per_request (int): Number of Series to delete per request.

            Returns:
                List[Union[Series, int]]: List of Series that could not be found in Sonarr.
        """
        valid_ids, invalid_ids = self._validate_tvdb_ids(ids)
        if len(valid_ids) > 0:
            json = {
                "deleteFiles": deleteFiles,
                "addImportExclusion": addImportExclusion
            }
            if per_request is None:
                per_request = len(valid_ids)
            for i in range(0, len(valid_ids), per_request):
                json["seriesIds"] = valid_ids[i:i+per_request]
                self._raw.delete_series_editor(json)
        return invalid_ids

    def language_profile(self) -> List[LanguageProfile]:
        """ Gets every :class:`~arrapi.objs.reload.LanguageProfile` in Sonarr.

            Returns:
                List[:class:`~arrapi.objs.reload.LanguageProfile`]: List of all Language Profiles
        """
        return [LanguageProfile(self, data) for data in self._raw.get_languageProfile()]

    def _validate_language_profile(self, language_profile):
        """ Validate Quality Profile options. """
        options = []
        for profile in self.language_profile():
            options.append(profile)
            if (isinstance(language_profile, LanguageProfile) and profile.id == language_profile.id) \
                    or (isinstance(language_profile, int) and profile.id == language_profile) \
                    or (profile.name == language_profile):
                return profile.id
        raise Invalid(f"Invalid Language Profile: '{language_profile}' Options: {options}")

