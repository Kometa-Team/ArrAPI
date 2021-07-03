from arrapi import util
from typing import Optional, Union, List, Tuple
from .api import BaseAPI
from .exceptions import NotFound, Invalid, Exists
from .objs import Movie, RootFolder, QualityProfile, Tag


class RadarrAPI(BaseAPI):
    """ Primary Class to use when connecting with the Radarr API

        Parameters:
            url (str): URL of Radarr application.
            apikey (str) apikey for the Radarr application.
     """

    def __init__(self, url: str, apikey: str) -> None:
        super().__init__(url, apikey)
        self.minimum_availability_options = ["announced", "inCinemas", "released", "preDB"]

    def _get_movie(self, tmdb_id=None):
        """ GET /movie """
        if tmdb_id is not None:
            return self._get("movie", **{"tmdbId": tmdb_id})
        else:
            return self._get("movie")

    def _get_movie_id(self, movie_id):
        """ GET /movie/{id} """
        return self._get(f"movie/{movie_id}")

    def _post_movie(self, json):
        """ POST /movie """
        return self._post("movie", json=json)

    def _post_movie_import(self, json):
        """ POST /movie/import """
        return self._post("movie/import", json=json)

    def _put_movie(self, json, moveFiles=False):
        """ PUT /movie """
        params = {"moveFiles": "true"} if moveFiles else {}
        return self._put("movie", json=json, **params)

    def _put_movie_id(self, movie_id, json, moveFiles=False):
        """ PUT /movie/{id} """
        params = {"moveFiles": "true"} if moveFiles else {}
        return self._put(f"movie/{movie_id}", json=json, **params)

    def _put_movie_editor(self, json):
        """ PUT /movie/editor """
        return self._put("movie/editor", json=json)

    def _delete_movie_id(self, movie_id, addImportExclusion=False, deleteFiles=False):
        """ DELETE /movie/{id} """
        params = {}
        if addImportExclusion:
            params["addImportExclusion"] = "true"
        if deleteFiles:
            params["deleteFiles"] = "true"
        self._delete(f"movie/{movie_id}", **params)

    def _delete_movie_editor(self, json):
        """ DELETE /movie/editor """
        return self._delete("movie/editor", json=json)

    def _get_movie_lookup(self, term):
        """ GET /movie/lookup """
        return self._get("movie/lookup", **{"term": term})

    def _validate_add_options(self, root_folder, quality_profile, monitor=True, search=True,
                              minimum_availability="announced", tags=None):
        """ Validate Add Movie options. """
        options = {
            "root_folder": self._validate_root_folder(root_folder),
            "quality_profile": self._validate_quality_profile(quality_profile),
            "monitor": True if monitor else False,
            "search": True if search else False,
            "minimum_availability": self._validate_minimum_availability(minimum_availability)
        }
        if tags:
            options["tags"] = self._validate_tags(tags)
        return options

    def _validate_edit_options(self, root_folder=None, path=None, move_files=False, quality_profile=None,
                               monitored=None, minimum_availability=None, tags=None, apply_tags="add"):
        """ Validate Edit Movie options. """
        if all(v is None for v in [root_folder, path, quality_profile, monitored, minimum_availability, tags]):
            raise ValueError("Expected either root_folder, path, quality_profile, "
                             "monitored, minimum_availability, or tags args")
        options = {"moveFiles": True if move_files else False}
        if root_folder is not None:
            options["rootFolderPath"] = self._validate_root_folder(root_folder)
        if path is not None:
            options["path"] = path
        if quality_profile is not None:
            options["qualityProfileId" if self.v3 else "profileId"] = self._validate_quality_profile(quality_profile)
        if monitored is not None:
            options["monitored"] = True if monitored else False
        if minimum_availability is not None:
            options["minimumAvailability"] = self._validate_minimum_availability(minimum_availability)
        if tags is not None:
            options["tags"] = self._validate_tags(tags, create=apply_tags != "remove")
            if apply_tags in self.apply_tags_options:
                options["applyTags"] = apply_tags
            else:
                raise Invalid(f"Invalid apply_tags: '{apply_tags}' Options: {self.apply_tags_options}")
        return options

    def _validate_minimum_availability(self, minimum_availability):
        """ Validate Minimum Availability options. """
        return util.validate_options("Minimum Availability", minimum_availability, self.minimum_availability_options)

    def _validate_tmdb_ids(self, tmdb_ids):
        """ Validate TMDb IDs. """
        valid_ids = []
        invalid_ids = []
        tmdb_radarr_ids = {m.tmdbId: m for m in self.all_movies()}
        for tmdb_id in tmdb_ids:
            if isinstance(tmdb_id, Movie):
                tmdb_id = tmdb_id.tmdbId
            if tmdb_id in tmdb_radarr_ids:
                valid_ids.append(tmdb_radarr_ids[tmdb_id].id)
            else:
                invalid_ids.append(tmdb_id)
        return valid_ids, invalid_ids

    def get_movie(self, movie_id: Optional[int] = None, tmdb_id: Optional[int] = None, imdb_id: Optional[str] = None) -> Movie:
        """ Gets a :class:`~arrapi.objs.Movie` by one of the IDs.

            Parameters:
                movie_id (Optional[int]): Search by Radarr Movie ID.
                tmdb_id (Optional[int]): Search by TMDb ID.
                imdb_id (Optional[int]): Search by IMDb ID.

            Returns:
                :class:`~arrapi.objs.Movie`: Movie for the ID given.

            Raises:
                :class:`ValueError`: When no ID is given.
                :class:`~arrapi.exceptions.NotFound`: When there's no movie with that ID.
        """
        if all(v is None for v in [movie_id, tmdb_id, imdb_id]):
            raise ValueError("Expected either movie_id, tmdb_id or imdb_id args")
        return Movie(self, movie_id=movie_id, tmdb_id=tmdb_id, imdb_id=imdb_id)

    def all_movies(self) -> List[Movie]:
        """ Gets all :class:`~arrapi.objs.Movie` in Radarr.

            Returns:
                List[:class:`~arrapi.objs.Movie`]: List of Movies in Radarr.
        """
        return [Movie(self, data=d) for d in self._get_movie()]

    def search_movies(self, term: str) -> List[Movie]:
        """ Gets a list of :class:`~arrapi.objs.Movie` by a search term.

            Parameters:
                term (str): Term to Search for.

            Returns:
                List[:class:`~arrapi.objs.Movie`]: List of Movie's found.
        """
        return [Movie(self, data=d) for d in self._get_movie_lookup(term)]

    def add_multiple_movies(self, tmdb_ids: List[Union[Movie, int]],
                            root_folder: Union[str, int, RootFolder],
                            quality_profile: Union[str, int, QualityProfile],
                            monitor: bool = True,
                            search: bool = True,
                            minimum_availability: str = "announced",
                            tags: Optional[List[Union[str, int, Tag]]] = None
                            ) -> Tuple[List[Movie], List[Movie], List[int]]:
        """ Adds multiple Movies to Radarr in a single call by their TMDb IDs.

            Parameters:
                tmdb_ids (List[Union[int, Movie]]): List of TMDB IDs or Movie lookups to add.
                root_folder (Union[str, int, RootFolder]): Root Folder for the Movies.
                quality_profile (Union[str, int, QualityProfile]): Quality Profile for the Movies.
                monitor (bool): Monitor the Movies.
                search (bool): Search for the Movies after adding.
                minimum_availability (str): Minimum Availability for the Movies. Valid options are announced, inCinemas, released, or preDB.
                tags (Optional[List[Union[str, int, Tag]]]): Tags to be added to the Movies.

            Returns:
                Tuple[List[:class:`~arrapi.objs.Movie`], List[:class:`~arrapi.objs.Movie`], List[int]]: List of Movies that were able to be added, List of Movies already in Radarr, List of TMDb IDs of Movies that could not be found.

            Raises:
                :class:`~arrapi.exceptions.Invalid`: When one of the options given is invalid.
        """
        options = self._validate_add_options(root_folder, quality_profile, monitor=monitor, search=search,
                                             minimum_availability=minimum_availability, tags=tags)
        json = []
        not_found_ids = []
        existing_movies = []
        for tmdb_id in tmdb_ids:
            try:
                movie = tmdb_id if isinstance(tmdb_id, Movie) else self.get_movie(tmdb_id=tmdb_id)
                try:
                    json.append(movie._get_add_data(options))
                except Exists:
                    existing_movies.append(movie)
            except NotFound:
                not_found_ids.append(tmdb_id)
        movies = [Movie(self, data=m) for m in self._post_movie_import(json)] if len(json) > 0 else []
        return movies, existing_movies, not_found_ids

    def edit_multiple_movies(self, tmdb_ids: List[Union[int, Movie]],
                             root_folder: Optional[Union[str, int, RootFolder]] = None,
                             move_files: bool = False,
                             quality_profile: Optional[Union[str, int, QualityProfile]] = None,
                             monitored: Optional[bool] = None,
                             minimum_availability: Optional[str] = None,
                             tags: Optional[List[Union[str, int, Tag]]] = None,
                             apply_tags: str = "add"
                             ) -> Tuple[List[Movie], List[int]]:
        """ Edit multiple Movies in Radarr by their TMDb IDs.

            Parameters:
                tmdb_ids (List[Union[int, Movie]]): List of TMDb IDs or Movie objects you want to edit.
                root_folder (Union[str, int, RootFolder]): Root Folder to change the Movie to.
                move_files (bool): When changing the root folder do you want to move the files to the new path.
                quality_profile (Optional[Union[str, int, QualityProfile]]): Quality Profile to change the Movie to.
                monitored (Optional[bool]): Monitor the Movie.
                minimum_availability (Optional[str]): Minimum Availability to change the Movie to. Valid options are announced, inCinemas, released, or preDB.
                tags (Optional[List[Union[str, int, Tag]]]): Tags to be added, replaced, or removed from the Movie.
                apply_tags (str): How you want to edit the Tags. Valid options are add, replace, or remove.

            Returns:
                Tuple[List[:class:`~arrapi.objs.Movie`], List[int]]: List of Movies that were able to be edited, List of TMDb IDs that could not be found in Radarr.

            Raises:
                :class:`~arrapi.exceptions.Invalid`: When one of the options given is invalid.
        """
        json = self._validate_edit_options(root_folder=root_folder, move_files=move_files,
                                           quality_profile=quality_profile, monitored=monitored,
                                           minimum_availability=minimum_availability, tags=tags, apply_tags=apply_tags)
        movie_list = []
        valid_ids, invalid_ids = self._validate_tmdb_ids(tmdb_ids)
        if len(valid_ids) > 0:
            json["movieIds"] = valid_ids
            movie_list = [Movie(self, data=m) for m in self._put_movie_editor(json)]
        return movie_list, invalid_ids

    def delete_multiple_movies(self, tmdb_ids: List[Union[int, Movie]],
                               addImportExclusion: bool = False,
                               deleteFiles: bool = False
                               ) -> List[int]:
        """ Deletes multiple Movies in Radarr by their TMDb IDs.

            Parameters:
                tmdb_ids (List[Union[int, Movie]]): List of TMDb IDs or Movie objects you want to delete.
                addImportExclusion (bool): Add Import Exclusion for these TMDb IDs.
                deleteFiles (bool): Delete Files for these TMDb IDs.

            Returns:
                List[int]: List of TMDb IDs that could not be found in Radarr.
        """
        valid_ids, invalid_ids = self._validate_tmdb_ids(tmdb_ids)
        if len(valid_ids) > 0:
            json = {
                "movieIds": valid_ids,
                "deleteFiles": deleteFiles,
                "addImportExclusion": addImportExclusion
            }
            self._delete_movie_editor(json)
        return invalid_ids
