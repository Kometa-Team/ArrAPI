import os, unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from arrapi import RadarrAPI, NotFound, Exists
from arrapi.objs.reload import Movie, Tag
from arrapi.objs.simple import Queue, RadarrExclusion, _paginate
from arrapi.raws.radarr import RadarrRawAPI
"""
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
"""
class RadarrTests(unittest.TestCase):
    radarr = None
    root = "/config"
    profile = "HD-1080p"
    profile2 = "HD - 720p/1080p"

    @classmethod
    def setUpClass(cls):
        cls.radarr = RadarrAPI(os.environ["RADARR_URL"], os.environ["RADARR_APIKEY"])
        has_config = False
        for rf in cls.radarr.root_folder():
            if rf.path == cls.root:
                has_config = True
        if not has_config:
            cls.radarr.add_root_folder(f"{cls.root}/")
        for movie in cls.radarr.all_movies():
            movie.delete()
        for tag in cls.radarr.all_tags():
            tag.delete()

    def test_lookups(self):
        movie = self.radarr.get_movie(imdb_id="tt0080684")
        self.assertEqual(movie.title, "The Empire Strikes Back")
        self.assertEqual(movie.tmdbId, 1891)
        self.assertEqual(movie.imdbId, "tt0080684")
        search = self.radarr.search_movies("Return of the Jedi")
        self.assertEqual(search[0].title, "Return of the Jedi")

    def get_test_movies(self):
        return [movie for movie in self.radarr.all_movies() if movie.tmdbId in [11, 1891, 1892, 1893, 1894, 1895]]

    def test_multiple_add_edit_delete(self):
        movie_ids = [self.radarr.get_movie(tmdb_id=11), "tt0080684", 1892, 1893, 1894, 1895]
        self.radarr.add_multiple_movies(movie_ids, self.root, self.profile, tags=["firsttag"])
        test_movies = self.get_test_movies()
        tmdb_ids = [movie.tmdbId for movie in test_movies]
        self.assertIn(11, tmdb_ids)
        self.assertIn(1891, tmdb_ids)
        self.assertIn(1892, tmdb_ids)
        self.assertIn(1893, tmdb_ids)
        self.assertIn(1894, tmdb_ids)
        self.assertIn(1895, tmdb_ids)
        for movie in test_movies:
            self.assertEqual(len(movie.tags), 1)
            self.assertEqual(movie.tags[0].label, "firsttag")
        movie_ids[0].reload()
        self.radarr.edit_multiple_movies(movie_ids, tags=["secondtag"], apply_tags="replace")
        for movie in self.get_test_movies():
            self.assertEqual(len(movie.tags), 1)
            self.assertEqual(movie.tags[0].label, "secondtag")
        self.radarr.delete_multiple_movies(movie_ids)
        self.assertEqual(len(self.get_test_movies()), 0)

    def test_single_add_edit_delete(self):
        movie = self.radarr.get_movie(tmdb_id=11)
        with self.assertRaises(NotFound):
            movie.delete()
        self.assertEqual(movie.title, "Star Wars")
        self.assertEqual(movie.tmdbId, 11)
        self.assertIsNone(movie.id)
        movie.add(self.root, self.profile, tags=["arrapi"])
        with self.assertRaises(Exists):
            movie.add(self.root, self.profile)
        self.assertIsNotNone(movie.id)
        movie = self.radarr.get_movie(movie_id=movie.id)
        self.assertGreater(len(movie.tags), 0)
        self.assertEqual(movie.tags[0].label, "arrapi")
        self.assertEqual(movie.minimumAvailability, "announced")
        self.assertEqual(movie.qualityProfile.name, self.profile)
        movie.edit(minimum_availability="released", quality_profile=self.profile2, tags=["arrapi"], apply_tags="remove")
        self.assertEqual(len(movie.tags), 0)
        self.assertEqual(movie.minimumAvailability, "released")
        self.assertEqual(movie.qualityProfile.name, self.profile2)
        movie.delete()
        self.assertIsNone(movie.id)
        with self.assertRaises(NotFound):
            movie.delete()

    def test_tag_edit(self):
        tag = next((t for t in self.radarr.all_tags() if t.label == "arrapi"), None)
        self.assertIsNotNone(tag)
        tag.edit("newtag")
        tag = next((t for t in self.radarr.all_tags() if t.label == "newtag"), None)
        self.assertIsNotNone(tag)


def _fake_arr(raw):
    return SimpleNamespace(_raw=raw)


class RadarrFeatureTests(unittest.TestCase):
    def test_pagination_stops_when_total_records_reached(self):
        getter = MagicMock(side_effect=[
            {"records": [{"tmdbId": 1}, {"tmdbId": 2}], "totalRecords": 3},
            {"records": [{"tmdbId": 3}], "totalRecords": 3},
        ])

        result = list(_paginate(getter, page_size=2))

        self.assertEqual([record["tmdbId"] for record in result], [1, 2, 3])
        self.assertEqual(getter.call_count, 2)
        getter.assert_any_call(page=1, pageSize=2)
        getter.assert_any_call(page=2, pageSize=2)

    def test_pagination_stops_on_short_or_empty_response(self):
        short_getter = MagicMock(side_effect=[
            {"records": [{"tmdbId": 1}, {"tmdbId": 2}]},
            {"records": [{"tmdbId": 3}]},
        ])
        none_getter = MagicMock(return_value=None)

        self.assertEqual([record["tmdbId"] for record in _paginate(short_getter, page_size=2)], [1, 2, 3])
        self.assertEqual(list(_paginate(none_getter, page_size=10)), [])
        self.assertEqual(short_getter.call_count, 2)
        none_getter.assert_called_once_with(page=1, pageSize=10)

    def test_exclusions_use_paged_or_legacy_endpoint(self):
        paged_raw = MagicMock(new_codebase=True)
        paged_raw.get_exclusions_paged.side_effect = [
            {"records": [{"tmdbId": 11, "movieTitle": "Star Wars", "movieYear": 1977}], "totalRecords": 2},
            {"records": [{"tmdbId": 1891, "movieTitle": "The Empire Strikes Back", "movieYear": 1980}], "totalRecords": 2},
        ]
        legacy_raw = MagicMock(new_codebase=False)
        legacy_raw.get_exclusions.return_value = [{"tmdbId": 1, "movieTitle": "Old", "movieYear": 1999}]

        self.assertEqual([ex.tmdbId for ex in RadarrExclusion.get_all(_fake_arr(paged_raw))], [11, 1891])
        self.assertEqual([ex.tmdbId for ex in RadarrExclusion.get_all(_fake_arr(legacy_raw))], [1])
        paged_raw.get_exclusions.assert_not_called()
        legacy_raw.get_exclusions_paged.assert_not_called()

    def test_queue_loads_all_pages_and_removes_an_item(self):
        raw = MagicMock(new_codebase=True)
        raw.get_queue.return_value = {"records": [{"id": 1, "title": "Example", "status": "downloading"}], "totalRecords": 1}

        queue = Queue.get_all(_fake_arr(raw))
        queue[0].remove(blocklist=True)

        self.assertEqual([(item.id, item.title, item.status) for item in queue], [(1, "Example", "downloading")])
        raw.get_queue.assert_called_once_with(page=1, pageSize=250)
        raw.delete_queue_id.assert_called_once_with(
            1, removeFromClient=True, blocklist=True, skipRedownload=False, changeCategory=False
        )

    def test_calendar_converts_tag_filters(self):
        raw = MagicMock()
        api = SimpleNamespace(_raw=raw, _validate_tags=MagicMock(return_value=[2, 3]))
        raw.get_calendar.return_value = []

        RadarrAPI.calendar(api, start="2026-01-01", end="2026-01-31", tags=[2, 3])

        api._validate_tags.assert_called_once_with([2, 3], create=False)
        raw.get_calendar.assert_called_once_with(
            start="2026-01-01", end="2026-01-31", unmonitored=False, tags="2,3"
        )

    def test_raw_feature_endpoints_make_direct_requests(self):
        raw = object.__new__(RadarrRawAPI)
        raw._get = MagicMock()
        raw._delete = MagicMock()

        raw.get_calendar(start="a", end="b", tags="1")
        raw.get_exclusions_paged(page=2, pageSize=5, sortKey="title", sortDirection="ascending")
        raw.get_queue(page=2, pageSize=5, status="downloading")
        raw.delete_queue_bulk([1, 2], blocklist=True)

        raw._get.assert_any_call("calendar", unmonitored=False, start="a", end="b", tags="1")
        raw._get.assert_any_call("exclusions/paged", page=2, pageSize=5, sortKey="title", sortDirection="ascending")
        raw._get.assert_any_call("queue", page=2, pageSize=5, status="downloading")
        raw._delete.assert_called_once_with(
            "queue/bulk", json={"ids": [1, 2]}, removeFromClient=True, blocklist=True,
            skipRedownload=False, changeCategory=False
        )

    def test_v3_movie_exposes_root_folder(self):
        movie = Movie(_fake_arr(SimpleNamespace(new_codebase=True)), data={"title": "Example", "rootFolderPath": "/movies"})

        self.assertEqual(movie.root_folder, "/movies")

    def test_tag_connections_loads_tag_details(self):
        raw = MagicMock()
        raw.get_tag_id.return_value = {
            "id": 3, "label": "connected", "delayProfileIds": [],
            "notificationIds": [10, 11], "restrictionIds": [], "importListIds": []
        }
        tag = Tag(_fake_arr(raw), {"id": 3, "label": "connected"})

        self.assertEqual(tag.connections, 2)
        raw.get_tag_id.assert_called_once_with(3, detail=True)





