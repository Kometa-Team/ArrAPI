from requests import Session
from typing import Optional, Union, List, Tuple
from arrapi import RootFolder, QualityProfile, Movie, Tag, NotFound, Invalid, Exists
from .base import BaseAPI
from ..objs.simple import RadarrExclusion
from ..raws.radarr import RadarrRawAPI


class RadarrAPI(BaseAPI):
    """ Primary Class to use when connecting with the Radarr API

        Parameters:
            url (str): URL of Radarr application.
            apikey (str): apikey for the Radarr application.
            session (Optional[Session]): Session object to use.
     """

    def __init__(self, url: str, apikey: str, session: Optional[Session] = None) -> None:
        super().__init__(RadarrRawAPI(url, apikey, session=session))
        self.exclusions = []
        self.minimum_availability_options = ["announced", "inCinemas", "released", "preDB"]

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
            options["qualityProfileId" if self._raw.v3 else "profileId"] = self._validate_quality_profile(quality_profile)
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
        return self._validate_options("Minimum Availability", minimum_availability, self.minimum_availability_options)

    def _validate_ids(self, ids):
        """ Validate IDs. """
        valid_ids = []
        invalid_ids = []
        radarr_ids = {}
        for m in self.all_movies():
            radarr_ids[m.tmdbId] = m
            radarr_ids[str(m.tmdbId)] = m
            radarr_ids[m.imdbId] = m
        for _id in ids:
            if isinstance(_id, Movie):
                valid_ids.append(_id.id)
            elif _id in radarr_ids:
                valid_ids.append(radarr_ids[_id].id)
            else:
                invalid_ids.append(_id)
        return valid_ids, invalid_ids

    def respect_list_exclusions_when_adding(self):
        """ Stores all List Exclusions so whenever :func:`~arrapi.objs.reload.Movie.add` or :func:`~arrapi.apis.sonarr.RadarrAPI.add_multiple_movies` is called the additions will be checked against the Exclusion List  """
        self.exclusions = [RadarrExclusion(self, ex).tmdbId for ex in self._raw.get_exclusions()]

    def get_movie(self, movie_id: Optional[int] = None, tmdb_id: Optional[int] = None, imdb_id: Optional[str] = None) -> Movie:
        """ Gets a :class:`~arrapi.objs.reload.Movie` by one of the IDs.

            Parameters:
                movie_id (Optional[int]): Search by Radarr Movie ID.
                tmdb_id (Optional[int]): Search by TMDb ID.
                imdb_id (Optional[int]): Search by IMDb ID.

            Returns:
                :class:`~arrapi.objs.reload.Movie`: Movie for the ID given.

            Raises:
                :class:`ValueError`: When no ID is given.
                :class:`~arrapi.exceptions.NotFound`: When there's no movie with that ID.
        """
        if all(v is None for v in [movie_id, tmdb_id, imdb_id]):
            raise ValueError("Expected either movie_id, tmdb_id or imdb_id args")
        return Movie(self, movie_id=movie_id, tmdb_id=tmdb_id, imdb_id=imdb_id)

    def all_movies(self) -> List[Movie]:
        """ Gets all :class:`~arrapi.objs.reload.Movie` in Radarr.

            Returns:
                List[:class:`~arrapi.objs.reload.Movie`]: List of Movies in Radarr.
        """
        return [Movie(self, data=d) for d in self._raw.get_movie()]

    def search_movies(self, term: str) -> List[Movie]:
        """ Gets a list of :class:`~arrapi.objs.reload.Movie` by a search term.

            Parameters:
                term (str): Term to Search for.

            Returns:
                List[:class:`~arrapi.objs.reload.Movie`]: List of Movie's found.
        """
        return [Movie(self, data=d) for d in self._raw.get_movie_lookup(term)]

    def add_movie(
            self,
            root_folder: Union[str, int, "RootFolder"],
            quality_profile: Union[str, int, "QualityProfile"],
            movie_id: Optional[int] = None,
            tmdb_id: Optional[int] = None,
            imdb_id: Optional[str] = None,
            monitor: bool = True,
            search: bool = True,
            minimum_availability: str = "announced",
            tags: Optional[List[Union[str, int, Tag]]] = None
            ) -> Movie:
        """ Gets a :class:`~arrapi.objs.reload.Movie` by one of the IDs and adds it to Radarr.

            Parameters:
                root_folder (Union[str, int, RootFolder]): Root Folder for the Movie.
                quality_profile (Union[str, int, QualityProfile]): Quality Profile for the Movie.
                movie_id (Optional[int]): Search by Radarr Movie ID.
                tmdb_id (Optional[int]): Search by TMDb ID.
                imdb_id (Optional[int]): Search by IMDb ID.
                monitor (bool): Monitor the Movie.
                search (bool): Search for the Movie after adding.
                minimum_availability (str): Minimum Availability for the Movie. Valid options are announced, inCinemas, released, or preDB.
                tags (Optional[List[Union[str, int, Tag]]]): Tags to be added to the Movie.

            Returns:
                :class:`~arrapi.objs.reload.Movie`: Movie for the ID given.

            Raises:
                :class:`ValueError`: When no ID is given.
                :class:`~arrapi.exceptions.NotFound`: When there's no movie with that ID.
                :class:`~arrapi.exceptions.Invalid`: When one of the options given is invalid.
                :class:`~arrapi.exceptions.Exists`: When the Movie already Exists in Radarr.
        """
        movie = self.get_movie(movie_id=movie_id, tmdb_id=tmdb_id, imdb_id=imdb_id)
        movie.add(root_folder, quality_profile, monitor=monitor, search=search,
                  minimum_availability=minimum_availability, tags=tags)
        return movie

    def edit_movie(
            self,
            movie_id: Optional[int] = None,
            tmdb_id: Optional[int] = None,
            imdb_id: Optional[str] = None,
            path: Optional[str] = None,
            move_files: bool = False,
            quality_profile: Optional[Union[str, int, "QualityProfile"]] = None,
            monitored: Optional[bool] = None,
            minimum_availability: Optional[str] = None,
            tags: Optional[List[Union[str, int, Tag]]] = None,
            apply_tags: str = "add"
            ) -> Movie:
        """ Gets a :class:`~arrapi.objs.reload.Movie` by one of the IDs and edits it in Radarr.

            Parameters:
                movie_id (Optional[int]): Search by Radarr Movie ID.
                tmdb_id (Optional[int]): Search by TMDb ID.
                imdb_id (Optional[int]): Search by IMDb ID.
                path (Optional[str]): Path to change the Movie to.
                move_files (bool): When changing the path do you want to move the files to the new path.
                quality_profile (Optional[Union[str, int, QualityProfile]]): Quality Profile to change the Movie to.
                monitored (Optional[bool]): Monitor the Movie.
                minimum_availability (Optional[str]): Minimum Availability to change the Movie to. Valid options are announced, inCinemas, released, or preDB.
                tags (Optional[List[Union[str, int, Tag]]]): Tags to be added, replaced, or removed from the Movie.
                apply_tags (str): How you want to edit the Tags. Valid options are add, replace, or remove.

            Raises:
                :class:`ValueError`: When no ID is given or when theres no options given.
                :class:`~arrapi.exceptions.Invalid`: When one of the options given is invalid.
                :class:`~arrapi.exceptions.NotFound`: When there's no movie with that ID or when the Movie hasn't been added to Radarr.
        """
        movie = self.get_movie(movie_id=movie_id, tmdb_id=tmdb_id, imdb_id=imdb_id)
        movie.edit(path=path, move_files=move_files, quality_profile=quality_profile, monitored=monitored,
                   minimum_availability=minimum_availability, tags=tags, apply_tags=apply_tags)
        return movie

    def delete_movie(
            self,
            movie_id: Optional[int] = None,
            tmdb_id: Optional[int] = None,
            imdb_id: Optional[str] = None,
            addImportExclusion: bool = False,
            deleteFiles: bool = False
    ) -> Movie:
        """ Gets a :class:`~arrapi.objs.reload.Movie` by one of the IDs and deletes it from Radarr.

            Parameters:
                movie_id (Optional[int]): Search by Radarr Movie ID.
                tmdb_id (Optional[int]): Search by TMDb ID.
                imdb_id (Optional[int]): Search by IMDb ID.
                addImportExclusion (bool): Add Import Exclusion for this Movie.
                deleteFiles (bool): Delete Files for this Movie.

            Returns:
                :class:`~arrapi.objs.reload.Movie`: Movie for the ID given.

            Raises:
                :class:`ValueError`: When no ID is given.
                :class:`~arrapi.exceptions.NotFound`: When there's no movie with that ID or when the Movie hasn't been added to Radarr.
        """
        movie = self.get_movie(movie_id=movie_id, tmdb_id=tmdb_id, imdb_id=imdb_id)
        movie.delete(addImportExclusion=addImportExclusion, deleteFiles=deleteFiles)
        return movie

    def add_multiple_movies(self, ids: List[Union[int, str, Movie, Tuple[Union[int, str, Movie], str]]],
                            root_folder: Union[str, int, RootFolder],
                            quality_profile: Union[str, int, QualityProfile],
                            monitor: bool = True,
                            search: bool = True,
                            minimum_availability: str = "announced",
                            tags: Optional[List[Union[str, int, Tag]]] = None,
                            per_request: int = None
                            ) -> Tuple[List[Movie], List[Movie], List[Union[int, str, Movie]]]:
        """ Adds multiple Movies to Radarr in a single call by their TMDb IDs.

            You can specify the path for each TMDb ID using a tuple in the list instead of just the ID ex. ``(11, "/media/Star Wars (1977)/")``

            The path provided must begin with the root_folder specified.

            Parameters:
                ids (List[Union[int, str, Movie, Tuple[Union[int, str, Movie], str]]]): List of TMDB IDs, IMDb IDs, or Movie lookups to add.
                root_folder (Union[str, int, RootFolder]): Root Folder for the Movies.
                quality_profile (Union[str, int, QualityProfile]): Quality Profile for the Movies.
                monitor (bool): Monitor the Movies.
                search (bool): Search for the Movies after adding.
                minimum_availability (str): Minimum Availability for the Movies. Valid options are announced, inCinemas, released, or preDB.
                tags (Optional[List[Union[str, int, Tag]]]): Tags to be added to the Movies.
                per_request (int): Number of Movies to add per request.

            Returns:
                Tuple[List[:class:`~arrapi.objs.reload.Movie`], List[:class:`~arrapi.objs.reload.Movie`], List[Union[int, str, Movie]]]: List of Movies that were able to be added, List of Movies already in Radarr, List of Movies that could not be found or were excluded.

            Raises:
                :class:`~arrapi.exceptions.Invalid`: When one of the options given is invalid.
        """
        options = self._validate_add_options(root_folder, quality_profile, monitor=monitor, search=search,
                                             minimum_availability=minimum_availability, tags=tags)
        json = []
        movies = []
        existing_movies = []
        invalid_ids = []
        for item in ids:
            path = item[1] if isinstance(item, tuple) else None
            item = item[0] if isinstance(item, tuple) else item
            try:
                if isinstance(item, Movie):
                    movie = item
                elif str(item).startswith("tt"):
                    movie = self.get_movie(imdb_id=item)
                else:
                    if self.exclusions and int(item) in self.exclusions:
                        raise NotFound
                    movie = self.get_movie(tmdb_id=item)
                if self.exclusions and movie.tmdbId in self.exclusions:
                    raise NotFound
                try:
                    json.append(movie._get_add_data(options, path=path))
                except Exists:
                    existing_movies.append(movie)
            except NotFound:
                invalid_ids.append(item)
        if len(json) > 0:
            if per_request is None:
                per_request = len(json)
            for i in range(0, len(json), per_request):
                movies.extend([Movie(self, data=m) for m in self._raw.post_movie_import(json[i:i+per_request])])
        return movies, existing_movies, invalid_ids

    def edit_multiple_movies(self, ids: List[Union[int, str, Movie]],
                             root_folder: Optional[Union[str, int, RootFolder]] = None,
                             move_files: bool = False,
                             quality_profile: Optional[Union[str, int, QualityProfile]] = None,
                             monitored: Optional[bool] = None,
                             minimum_availability: Optional[str] = None,
                             tags: Optional[List[Union[str, int, Tag]]] = None,
                             apply_tags: str = "add",
                             per_request: int = None
                             ) -> Tuple[List[Movie], List[Union[int, str, Movie]]]:
        """ Edit multiple Movies in Radarr by their TMDb IDs.

            Parameters:
                ids (List[Union[int, str, Movie]]): List of TMDb IDs, IMDb IDs, or Movie objects you want to edit.
                root_folder (Union[str, int, RootFolder]): Root Folder to change the Movie to.
                move_files (bool): When changing the root folder do you want to move the files to the new path.
                quality_profile (Optional[Union[str, int, QualityProfile]]): Quality Profile to change the Movie to.
                monitored (Optional[bool]): Monitor the Movie.
                minimum_availability (Optional[str]): Minimum Availability to change the Movie to. Valid options are announced, inCinemas, released, or preDB.
                tags (Optional[List[Union[str, int, Tag]]]): Tags to be added, replaced, or removed from the Movie.
                apply_tags (str): How you want to edit the Tags. Valid options are add, replace, or remove.
                per_request (int): Number of Movies to edit per request.

            Returns:
                Tuple[List[:class:`~arrapi.objs.reload.Movie`], List[Union[int, str, Movie]]]: List of Movies that were able to be edited, List of Movies that could not be found in Radarr.

            Raises:
                :class:`~arrapi.exceptions.Invalid`: When one of the options given is invalid.
        """
        json = self._validate_edit_options(root_folder=root_folder, move_files=move_files,
                                           quality_profile=quality_profile, monitored=monitored,
                                           minimum_availability=minimum_availability, tags=tags, apply_tags=apply_tags)
        movie_list = []
        valid_ids, invalid_ids = self._validate_ids(ids)
        if len(valid_ids) > 0:
            if per_request is None:
                per_request = len(valid_ids)
            for i in range(0, len(valid_ids), per_request):
                json["movieIds"] = valid_ids[i:i+per_request]
                movie_list = [Movie(self, data=m) for m in self._raw.put_movie_editor(json)]
        return movie_list, invalid_ids

    def delete_multiple_movies(self, ids: List[Union[int, str, Movie]],
                               addImportExclusion: bool = False,
                               deleteFiles: bool = False,
                               per_request: int = None
                               ) -> List[Union[int, str, Movie]]:
        """ Deletes multiple Movies in Radarr by their TMDb IDs.

            Parameters:
                ids (List[Union[int, str, Movie]]): List of TMDb IDs, IMDb IDs, or Movie objects you want to delete.
                addImportExclusion (bool): Add Import Exclusion for these TMDb IDs.
                deleteFiles (bool): Delete Files for these TMDb IDs.
                per_request (int): Number of Movies to delete per request.

            Returns:
                List[Union[int, str, Movie]]: List of Movies that could not be found in Radarr.
        """
        valid_ids, invalid_ids = self._validate_ids(ids)
        if len(valid_ids) > 0:
            json = {
                "deleteFiles": deleteFiles,
                "addImportExclusion": addImportExclusion
            }
            if per_request is None:
                per_request = len(valid_ids)
            for i in range(0, len(valid_ids), per_request):
                json["movieIds"] = valid_ids[i:i+per_request]
                self._raw.delete_movie_editor(json)
        return invalid_ids
