
Welcome to ArrAPI's documentation!
==========================================================

.. image:: https://img.shields.io/github/v/release/Kometa-Team/ArrAPI?style=plastic
    :target: https://github.com/Kometa-Team/ArrAPI/releases
    :alt: GitHub release (latest by date)

.. image:: https://img.shields.io/travis/com/Kometa-Team/ArrAPI?style=plastic
    :target: https://app.travis-ci.com/Kometa-Team/ArrAPI
    :alt: Build Testing

.. image:: https://img.shields.io/github/commits-since/Kometa-Team/ArrAPI/latest?style=plastic
    :target: https://github.com/Kometa-Team/ArrAPI/commits/master
    :alt: GitHub commits since latest release (by date) for a branch

.. image:: https://img.shields.io/pypi/v/ArrAPI?style=plastic
    :target: https://pypi.org/project/arrapi/
    :alt: PyPI

.. image:: https://img.shields.io/pypi/dm/arrapi.svg?style=plastic
    :target: https://pypi.org/project/arrapi/
    :alt: Downloads

|

.. image:: https://img.shields.io/readthedocs/arrapi?style=plastic
    :target: https://arrapi.kometa.wiki
    :alt: Wiki

.. image:: https://img.shields.io/discord/822460010649878528?color=%2300bc8c&label=Discord&style=plastic
    :target: https://kometa.wiki/en/latest/discord/
    :alt: Discord

.. image:: https://img.shields.io/reddit/subreddit-subscribers/Kometa?color=%2300bc8c&label=r%2FKometa&style=plastic
    :target: https://www.reddit.com/r/Kometa/
    :alt: Reddit

.. image:: https://img.shields.io/github/sponsors/meisnate12?color=%238a2be2&style=plastic
    :target: https://github.com/sponsors/meisnate12
    :alt: GitHub Sponsors

.. image:: https://img.shields.io/badge/-Sponsor_or_Donate-blueviolet?style=plastic
    :target: https://github.com/sponsors/Kometa-Team
    :alt: Sponsor or Donate

Overview
----------------------------------------------------------
Unofficial Python bindings for the Sonarr and Radarr APIs. The goal is to make interaction with the API as easy as possible while emulating the Web Client as much as possible


Installation & Documentation
----------------------------------------------------------

.. code-block:: python

    pip install arrapi

Documentation_ can be found at Read the Docs.

.. _Documentation: https://arrapi.kometa.wiki

Connecting to Sonarr
==========================================================

Getting a SonarrAPI Instance
----------------------------------------------------------

To connect to a Sonarr application you have to use the :class:`~arrapi.apis.sonarr.SonarrAPI` object and provide it with the ``baseurl`` and ``apikey`` parameters.

The ``apikey`` can be found by going to ``Settings > General > Security > API Key``

.. code-block:: python

    from arrapi import SonarrAPI

    baseurl = "http://192.168.1.12:8989"
    apikey = "0010843563404748808d3fc9c562c05e"

    sonarr = SonarrAPI(baseurl, apikey)

Using the SonarrAPI Instance
----------------------------------------------------------

Once you have a :class:`~arrapi.apis.sonarr.SonarrAPI` instance you can use it to interact with the application.

To add, edit, or delete a singular Series you must first find the :class:`~arrapi.objs.reload.Series` object.

Find a Series Object
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

There are three ways to find a :class:`~arrapi.objs.reload.Series` object.

You can get a :class:`~arrapi.objs.reload.Series` object using :meth:`~arrapi.apis.sonarr.SonarrAPI.get_series` and giving it a ``Sonarr Series ID`` or ``TVDb ID``.

.. code-block:: python

    series = sonarr.get_series(tvdb_id=121361)

You can get a ``List`` of :class:`~arrapi.objs.reload.Series` objects using :meth:`~arrapi.apis.sonarr.SonarrAPI.search_series` and giving it a search term.

.. code-block:: python

    search = sonarr.search_series("Game of Thrones")

You can get a ``List`` of all :class:`~arrapi.objs.reload.Series` objects in Sonarr using :meth:`~arrapi.apis.sonarr.SonarrAPI.all_series`.

.. code-block:: python

    all_series = sonarr.all_series()


Using a Series Object
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

To add a series to Sonarr use :meth:`~arrapi.objs.reload.Series.add`.

.. code-block:: python

    series.add("/shows/", "HD-1080p", "English")

To edit a series in Sonarr use :meth:`~arrapi.objs.reload.Series.edit`.

.. code-block:: python

    series.edit(tags=["hd"])

To delete a series in Sonarr use :meth:`~arrapi.objs.reload.Series.delete`.

.. code-block:: python

    series.delete()


Perform Operations on Multiple Series
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

To add multiple Series to Sonarr use :meth:`~arrapi.apis.sonarr.SonarrAPI.add_multiple_series` with the Series' TVDb IDs.

.. code-block:: python

    series_ids = [83268, 283468, 385376]
    added, exists, invalid = sonarr.add_multiple_series(series_ids, "/shows/", "HD-1080p", "English")

To edit multiple Series in Sonarr use :meth:`~arrapi.apis.sonarr.SonarrAPI.edit_multiple_series` with the Series' TVDb IDs.

.. code-block:: python

    series_ids = [83268, 283468, 385376]
    edited, not_exist = sonarr.edit_multiple_series(series_ids, monitor=False)

To delete multiple Series in Sonarr use :meth:`~arrapi.apis.sonarr.SonarrAPI.delete_multiple_series` with the Series' TVDb IDs.

.. code-block:: python

    series_ids = [83268, 283468, 385376]
    not_exist = sonarr.delete_multiple_series(series_ids)

Respect Sonarr List Exclusions
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

To respect Sonarr's List Exclusions, before running :meth:`~arrapi.objs.reload.Series.add` or :meth:`~arrapi.apis.sonarr.SonarrAPI.add_multiple_series` you can use :meth:`~arrapi.apis.sonarr.SonarrAPI.respect_list_exclusions_when_adding` like so.

.. code-block:: python

    series_ids = [83268, 283468, 385376]
    sonarr.respect_list_exclusions_when_adding()
    added, exists, invalid = sonarr.add_multiple_series(series_ids, "/shows/", "HD-1080p", "English")

Connecting to Radarr
==========================================================

Getting a RadarrAPI Instance
----------------------------------------------------------

To connect to a Radarr application you have to use the :class:`~arrapi.apis.radarr.RadarrAPI` object and provide it with the ``baseurl`` and ``apikey`` parameters.

The ``apikey`` can be found by going to ``Settings > General > Security > API Key``

.. code-block:: python

    from arrapi import RadarrAPI

    baseurl = "http://192.168.1.12:8989"
    apikey = "0010843563404748808d3fc9c562c05e"

    radarr = RadarrAPI(baseurl, apikey)

Using the RadarrAPI Instance
----------------------------------------------------------

Once you have a :class:`~arrapi.apis.radarr.RadarrAPI` instance you can use it to interact with the application.

To add, edit, or delete a singular Movie you must first find the :class:`~arrapi.objs.reload.Movie` object.

Find a Movie Object
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

There are three ways to find a :class:`~arrapi.objs.reload.Movie` object.

You can get a :class:`~arrapi.objs.reload.Movie` object using :meth:`~arrapi.apis.radarr.RadarrAPI.get_movie` and giving it a ``Radarr Movie ID`` or ``TVDb ID``.

.. code-block:: python

    movie = radarr.get_movie(tmdb_id=121361)

You can get a ``List`` of :class:`~arrapi.objs.reload.Movie` objects using :meth:`~arrapi.apis.radarr.RadarrAPI.search_movies` and giving it a search term.

.. code-block:: python

    search = radarr.search_movies("The Lord of the Rings: The Return of the King")

You can get a ``List`` of all :class:`~arrapi.objs.reload.Movie` objects in Radarr using :meth:`~arrapi.apis.radarr.RadarrAPI.all_movies`.

.. code-block:: python

    all_movies = radarr.all_movies()

Using a Movie Object
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

To add a movie to Radarr use :meth:`~arrapi.objs.reload.Movie.add`.

.. code-block:: python

    movie.add("/movies/", "HD-1080p")

To edit a movie in Radarr use :meth:`~arrapi.objs.reload.Movie.edit`.

.. code-block:: python

    movie.edit(tags=["hd"])

To delete a movie in Radarr use :meth:`~arrapi.objs.reload.Movie.delete`.

.. code-block:: python

    movie.delete()

Perform Operations on Multiple Movie
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

To add multiple Movies to Radarr use :meth:`~arrapi.apis.radarr.RadarrAPI.add_multiple_movies` with the Movie's TMDb IDs.

.. code-block:: python

    movie_ids = [11, 1891, 1892, 1893, 1894, 1895]
    added, exists, invalid = radarr.add_multiple_movies(movie_ids, "/movies/", "HD-1080p")

To edit multiple Movies in Radarr use :meth:`~arrapi.apis.radarr.RadarrAPI.edit_multiple_movies` with the Movie's TMDb IDs.

.. code-block:: python

    movie_ids = [11, 1891, 1892, 1893, 1894, 1895]
    edited, not_exist = radarr.edit_multiple_movies(movie_ids, monitor=False)

To delete multiple Movies in Radarr use :meth:`~arrapi.apis.radarr.RadarrAPI.delete_multiple_movies` with the Movie's TMDb IDs.

.. code-block:: python

    movie_ids = [11, 1891, 1892, 1893, 1894, 1895]
    not_exist = radarr.delete_multiple_movies(movie_ids)

Respect Radarr List Exclusions
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

To respect Radarr's List Exclusions, before running :meth:`~arrapi.objs.reload.Series.add` or :meth:`~arrapi.apis.sonarr.SonarrAPI.add_multiple_series` you can use :meth:`~arrapi.apis.sonarr.SonarrAPI.respect_list_exclusions_when_adding` like so.

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
* `Sonarr v3 API Docs <https://sonarr.tv/docs/api/>`_

Usage & Contributions
----------------------------------------------------------
* Source is available on the `Github Project Page <https://github.com/Kometa-Team/ArrAPI>`_.
* Contributors to ArrAPI own their own contributions and may distribute that code under
  the `MIT license <https://github.com/Kometa-Team/ArrAPI/blob/master/LICENSE.txt>`_.
