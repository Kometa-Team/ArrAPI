ArrAPI
==========================================================

.. image:: https://img.shields.io/travis/com/meisnate12/ArrAPI?style=plastic
    :target: https://app.travis-ci.com/meisnate12/ArrAPI
    :alt: Build Testing

.. image:: https://img.shields.io/readthedocs/arrapi?style=plastic
    :target: https://arrapi.metamanager.wiki
    :alt: Read the Docs

.. image:: https://img.shields.io/github/v/release/meisnate12/ArrAPI?style=plastic
    :target: https://github.com/meisnate12/ArrAPI/releases
    :alt: GitHub release (latest by date)

.. image:: https://img.shields.io/pypi/v/ArrAPI?style=plastic
    :target: https://pypi.org/project/arrapi/
    :alt: PyPI

.. image:: https://img.shields.io/pypi/dm/arrapi.svg?style=plastic
    :target: https://pypi.org/project/arrapi/
    :alt: Downloads

.. image:: https://img.shields.io/github/commits-since/meisnate12/ArrAPI/latest?style=plastic
    :target: https://github.com/meisnate12/ArrAPI/commits/master
    :alt: GitHub commits since latest release (by date) for a branch

.. image:: https://img.shields.io/badge/-Sponsor_or_Donate-blueviolet?style=plastic
    :target: https://github.com/sponsors/meisnate12
    :alt: GitHub Sponsor

Overview
----------------------------------------------------------
Unofficial Python bindings for the Sonarr and Radarr APIs. The goal is to make interaction with the API as easy as possible while emulating the Web Client as much as possible


Installation & Documentation
----------------------------------------------------------

.. code-block:: python

    pip install arrapi

Documentation_ can be found at Read the Docs.

.. _Documentation: https://arrapi.metamanager.wiki

Connecting to Sonarr
==========================================================

Getting a SonarrAPI Instance
----------------------------------------------------------

To connect to a Sonarr application you have to use the |SonarrAPI|_ object and provide it with the ``baseurl`` and ``apikey`` parameters.

The ``apikey`` can be found by going to ``Settings > General > Security > API Key``

.. code-block:: python

    from arrapi import SonarrAPI

    baseurl = "http://192.168.1.12:8989"
    apikey = "0010843563404748808d3fc9c562c05e"

    sonarr = SonarrAPI(baseurl, apikey)

Using the SonarrAPI Instance
----------------------------------------------------------

Once you have a |SonarrAPI|_ instance you can use it to interact with the application.

To add, edit, or delete a singular Series you must first find the |Series|_ object.

Find a Series Object
----------------------------------------------------------

There are three ways to find a |Series|_ object.

You can get a |Series|_ object using |get_series|_ and giving it a ``Sonarr Series ID`` or ``TVDb ID``.

.. code-block:: python

    series = sonarr.get_series(tvdb_id=121361)

You can get a ``List`` of |Series|_ objects using |search_series|_ and giving it a search term.

.. code-block:: python

    search = sonarr.search_series("Game of Thrones")

You can get a ``List`` of all |Series|_ objects in Sonarr using |all_series|_.

.. code-block:: python

    all_series = sonarr.all_series()

Using a Series Object
----------------------------------------------------------

To add a series to Sonarr use |sonarr_add|_.

.. code-block:: python

    series.add("/shows/", "HD-1080p", "English")

To edit a series in Sonarr use |sonarr_edit|_.

.. code-block:: python

    series.edit(tags=["hd"])

To delete a series in Sonarr use |sonarr_delete|_.

.. code-block:: python

    series.delete()

Perform Operations on Multiple Series
----------------------------------------------------------

To add multiple Series to Sonarr use |add_multiple_series|_ with the Series' TVDb IDs.

.. code-block:: python

    series_ids = [83268, 283468, 385376]
    added, exists, invalid = sonarr.add_multiple_series(series_ids, "/shows/", "HD-1080p", "English")

To edit multiple Series in Sonarr use |edit_multiple_series|_ with the Series' TVDb IDs.

.. code-block:: python

    series_ids = [83268, 283468, 385376]
    edited, not_exist = sonarr.edit_multiple_series(series_ids, monitor=False)

To delete multiple Series in Sonarr use |delete_multiple_series|_ with the Series' TVDb IDs.

.. code-block:: python

    series_ids = [83268, 283468, 385376]
    not_exist = sonarr.delete_multiple_series(series_ids)

Respect Sonarr List Exclusions
----------------------------------------------------------

To respect Sonarr's List Exclusions, before running |sonarr_add|_ or |add_multiple_series|_ you can use |sonarr_exclusions|_ like so.

.. code-block:: python

    series_ids = [83268, 283468, 385376]
    sonarr.respect_list_exclusions_when_adding()
    added, exists, invalid = sonarr.add_multiple_series(series_ids, "/shows/", "HD-1080p", "English")

Connecting to Radarr
==========================================================

Getting a RadarrAPI Instance
----------------------------------------------------------

To connect to a Radarr application you have to use the |RadarrAPI|_ object and provide it with the ``baseurl`` and ``apikey`` parameters.

The ``apikey`` can be found by going to ``Settings > General > Security > API Key``

.. code-block:: python

    from arrapi import RadarrAPI

    baseurl = "http://192.168.1.12:8989"
    apikey = "0010843563404748808d3fc9c562c05e"

    radarr = RadarrAPI(baseurl, apikey)

Using the RadarrAPI Instance
----------------------------------------------------------

Once you have a |RadarrAPI|_ instance you can use it to interact with the application.

To add, edit, or delete a singular Movie you must first find the |Movie|_ object.

Find a Movie Object
----------------------------------------------------------

There are three ways to find a |Movie|_ object.

You can get a |Movie|_ object using |get_movie|_ and giving it a ``Radarr Movie ID`` or ``TVDb ID``.

.. code-block:: python

    movie = radarr.get_movie(tmdb_id=121361)

You can get a ``List`` of |Movie|_ objects using |search_movies|_ and giving it a search term.

.. code-block:: python

    search = radarr.search_movies("The Lord of the Rings: The Return of the King")

You can get a ``List`` of all |Movie|_ objects in Radarr using |all_movies|_.

.. code-block:: python

    all_movies = radarr.all_movies()

Using a Movie Object
----------------------------------------------------------

To add a movie to Radarr use |radarr_add|_.

.. code-block:: python

    movie.add("/movies/", "HD-1080p")

To edit a movie in Radarr use |radarr_edit|_.

.. code-block:: python

    movie.edit(tags=["hd"])

To delete a movie in Radarr use |radarr_delete|_.

.. code-block:: python

    movie.delete()

Perform Operations on Multiple Movie
----------------------------------------------------------

To add multiple Movies to Radarr use |add_multiple_movies|_ with the Movie's TMDb IDs.

.. code-block:: python

    movie_ids = [11, 1891, 1892, 1893, 1894, 1895]
    added, exists, invalid = radarr.add_multiple_movies(movie_ids, "/movies/", "HD-1080p")

To edit multiple Movies in Radarr use |edit_multiple_movies|_ with the Movie's TMDb IDs.

.. code-block:: python

    movie_ids = [11, 1891, 1892, 1893, 1894, 1895]
    edited, not_exist = radarr.edit_multiple_movies(movie_ids, monitor=False)

To delete multiple Movies in Radarr use |delete_multiple_movies|_ with the Movie's TMDb IDs.

.. code-block:: python

    movie_ids = [11, 1891, 1892, 1893, 1894, 1895]
    not_exist = radarr.delete_multiple_movies(movie_ids)

Respect Radarr List Exclusions
----------------------------------------------------------

To respect Radarr's List Exclusions, before running |radarr_add|_ or |add_multiple_movies|_ you can use |radarr_exclusions|_ like so.

.. code-block:: python

    movie_ids = [11, 1891, 1892, 1893, 1894, 1895]
    radarr.respect_list_exclusions_when_adding()
    added, exists, invalid = radarr.add_multiple_movies(movie_ids, "/movies/", "HD-1080p")

Usage Examples
==========================================================

Example 1: List all series in Sonarr.

.. code-block:: python

    series = sonarr.all_series()
    for show in series:
        print(show.title)

Example 2: Search for a movie and add it to Radarr by name.

.. code-block:: python

    search = radarr.search_movies("The Lord of the Rings: The Return of the King")
    if search:
        search[0].add("/movies/", "HD-1080p")

Example 3: Make every series in Sonarr Unmonitored.

.. code-block:: python

    edited, not_exist = sonarr.edit_multiple_series(sonarr.all_series(), monitor=False)

Example 4: Get all Quality Profiles Available.

.. code-block:: python

    for qp in sonarr.quality_profile():
        print(qp.name)

Hyperlinks
----------------------------------------------------------

* `Radarr v3 API Docs <https://radarr.video/docs/api>`_
* `Sonarr API Docs <https://github.com/Sonarr/Sonarr/wiki/API>`_
* Theres no Docs for Sonarr v3 Yet.

.. |SonarrAPI| replace:: ``SonarrAPI``
.. _SonarrAPI: https://arrapi.metamanager.wiki/en/latest/sonarr.html#module-arrapi.sonarr

.. |Series| replace:: ``Series``
.. _Series: https://arrapi.metamanager.wiki/en/latest/objs.html#series

.. |get_series| replace:: ``get_series``
.. _get_series: https://arrapi.metamanager.wiki/en/latest/sonarr.html#arrapi.sonarr.SonarrAPI.get_series

.. |search_series| replace:: ``search_series``
.. _search_series: https://arrapi.metamanager.wiki/en/latest/sonarr.html#arrapi.sonarr.SonarrAPI.search_series

.. |all_series| replace:: ``all_series``
.. _all_series: https://arrapi.metamanager.wiki/en/latest/sonarr.html#arrapi.sonarr.SonarrAPI.all_series

.. |sonarr_add| replace:: ``add``
.. _sonarr_add: https://arrapi.metamanager.wiki/en/latest/objs.html#arrapi.objs.Series.add

.. |sonarr_edit| replace:: ``edit``
.. _sonarr_edit: https://arrapi.metamanager.wiki/en/latest/objs.html#arrapi.objs.Series.edit

.. |sonarr_delete| replace:: ``delete``
.. _sonarr_delete: https://arrapi.metamanager.wiki/en/latest/objs.html#arrapi.objs.Series.delete

.. |add_multiple_series| replace:: ``add_multiple_series``
.. _add_multiple_series: https://arrapi.metamanager.wiki/en/latest/sonarr.html#arrapi.sonarr.SonarrAPI.add_multiple_series

.. |edit_multiple_series| replace:: ``edit_multiple_series``
.. _edit_multiple_series: https://arrapi.metamanager.wiki/en/latest/sonarr.html#arrapi.sonarr.SonarrAPI.edit_multiple_series

.. |delete_multiple_series| replace:: ``delete_multiple_series``
.. _delete_multiple_series: https://arrapi.metamanager.wiki/en/latest/sonarr.html#arrapi.sonarr.SonarrAPI.delete_multiple_series

.. |sonarr_exclusions| replace:: ``sonarr_exclusions``
.. _sonarr_exclusions: https://arrapi.metamanager.wiki/en/latest/sonarr.html#arrapi.sonarr.SonarrAPI.respect_list_exclusions_when_adding

.. |RadarrAPI| replace:: ``RadarrAPI``
.. _RadarrAPI: https://arrapi.metamanager.wiki/en/latest/radarr.html#module-arrapi.radarr

.. |Movie| replace:: ``Movie``
.. _Movie: https://arrapi.metamanager.wiki/en/latest/objs.html#movie

.. |get_movie| replace:: ``get_movie``
.. _get_movie: https://arrapi.metamanager.wiki/en/latest/radarr.html#arrapi.radarr.RadarrAPI.get_movie

.. |search_movies| replace:: ``search_movies``
.. _search_movies: https://arrapi.metamanager.wiki/en/latest/radarr.html#arrapi.radarr.RadarrAPI.search_movies

.. |all_movies| replace:: ``all_movies``
.. _all_movies: https://arrapi.metamanager.wiki/en/latest/radarr.html#arrapi.radarr.RadarrAPI.all_movies

.. |radarr_add| replace:: ``add``
.. _radarr_add: https://arrapi.metamanager.wiki/en/latest/objs.html#arrapi.objs.Movie.add

.. |radarr_edit| replace:: ``edit``
.. _radarr_edit: https://arrapi.metamanager.wiki/en/latest/objs.html#arrapi.objs.Movie.edit

.. |radarr_delete| replace:: ``delete``
.. _radarr_delete: https://arrapi.metamanager.wiki/en/latest/objs.html#arrapi.objs.Movie.delete

.. |add_multiple_movies| replace:: ``add_multiple_movies``
.. _add_multiple_movies: https://arrapi.metamanager.wiki/en/latest/radarr.html#arrapi.radarr.RadarrAPI.add_multiple_movies

.. |edit_multiple_movies| replace:: ``edit_multiple_movies``
.. _edit_multiple_movies: https://arrapi.metamanager.wiki/en/latest/radarr.html#arrapi.radarr.RadarrAPI.edit_multiple_movies

.. |delete_multiple_movies| replace:: ``delete_multiple_movies``
.. _delete_multiple_movies: https://arrapi.metamanager.wiki/en/latest/radarr.html#arrapi.radarr.RadarrAPI.delete_multiple_movies

.. |radarr_exclusions| replace:: ``radarr_exclusions``
.. _radarr_exclusions: https://arrapi.metamanager.wiki/en/latest/radarr.html#arrapi.radarr.RadarrAPI.respect_list_exclusions_when_adding
