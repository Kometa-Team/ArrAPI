import os, unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from arrapi import SonarrAPI, NotFound, Exists
from arrapi.objs.reload import Tag
from arrapi.objs.simple import Episode, Queue, SonarrExclusion
from arrapi.raws.sonarr import SonarrRawAPI
"""
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
"""
class SonarrTests(unittest.TestCase):
    sonarr = None
    root = "/config"
    profile = "HD-1080p"
    profile2 = "HD - 720p/1080p"
    language = "English"

    @classmethod
    def setUpClass(cls):
        cls.sonarr = SonarrAPI(os.environ["SONARR_URL"], os.environ["SONARR_APIKEY"])
        has_config = False
        for rf in cls.sonarr.root_folder():
            if rf.path == cls.root:
                has_config = True
        if not has_config:
            cls.sonarr.add_root_folder(f"{cls.root}/")
        for series in cls.sonarr.all_series():
            series.delete()
        for tag in cls.sonarr.all_tags():
            tag.delete()

    def test_lookups(self):
        series = self.sonarr.get_series(tvdb_id=121361)
        self.assertEqual(series.title, "Game of Thrones")
        self.assertEqual(series.tvdbId, 121361)
        self.assertEqual(series.imdbId, "tt0944947")
        search = self.sonarr.search_series("Breaking Bad")
        self.assertEqual(search[0].title, "Breaking Bad")

    def get_test_series(self):
        return [series for series in self.sonarr.all_series() if series.tvdbId in [83268, 283468, 385376]]

    def test_multiple_add_edit_delete(self):
        series_ids = [self.sonarr.get_series(tvdb_id=83268), 283468, 385376]
        self.sonarr.add_multiple_series(series_ids, self.root, self.profile, self.language, tags=["firsttag"])
        test_series = self.get_test_series()
        tvdb_ids = [series.tvdbId for series in test_series]
        self.assertIn(83268, tvdb_ids)
        self.assertIn(283468, tvdb_ids)
        self.assertIn(385376, tvdb_ids)
        for series in test_series:
            self.assertEqual(len(series.tags), 1)
            self.assertEqual(series.tags[0].label, "firsttag")
        series_ids[0].reload()
        self.sonarr.edit_multiple_series(series_ids, tags=["secondtag"], apply_tags="replace")
        for series in self.get_test_series():
            self.assertEqual(len(series.tags), 1)
            self.assertEqual(series.tags[0].label, "secondtag")
        self.sonarr.delete_multiple_series(series_ids)
        self.assertEqual(len(self.get_test_series()), 0)

    def test_single_add_edit_delete(self):
        series = self.sonarr.get_series(tvdb_id=121361)
        with self.assertRaises(NotFound):
            series.delete()
        self.assertEqual(series.title, "Game of Thrones")
        self.assertEqual(series.tvdbId, 121361)
        self.assertIsNone(series.id)
        series.add(self.root, self.profile, self.language, tags=["arrapi"])
        with self.assertRaises(Exists):
            series.add(self.root, self.profile, self.language)
        self.assertIsNotNone(series.id)
        series = self.sonarr.get_series(series_id=series.id)
        self.assertGreater(len(series.tags), 0)
        self.assertEqual(series.tags[0].label, "arrapi")
        self.assertEqual(series.seriesType, "standard")
        self.assertEqual(series.qualityProfile.name, self.profile)
        series.edit(series_type="anime", quality_profile=self.profile2, tags=["arrapi"], apply_tags="remove")
        self.assertEqual(len(series.tags), 0)
        self.assertEqual(series.seriesType, "anime")
        self.assertEqual(series.qualityProfile.name, self.profile2)
        series.delete()
        self.assertIsNone(series.id)
        with self.assertRaises(NotFound):
            series.delete()

    def test_tag_edit(self):
        tag = next((t for t in self.sonarr.all_tags() if t.label == "arrapi"), None)
        self.assertIsNotNone(tag)
        tag.edit("newtag")
        tag = next((t for t in self.sonarr.all_tags() if t.label == "newtag"), None)
        self.assertIsNotNone(tag)


def _fake_arr(raw):
    return SimpleNamespace(_raw=raw)


class SonarrFeatureTests(unittest.TestCase):
    def test_exclusions_use_paged_or_legacy_endpoint(self):
        paged_raw = MagicMock(new_codebase=True)
        paged_raw.get_importlistexclusion_paged.side_effect = [
            {"records": [{"tvdbId": 100, "title": "Breaking Bad"}], "totalRecords": 2},
            {"records": [{"tvdbId": 200, "title": "The Wire"}], "totalRecords": 2},
        ]
        legacy_raw = MagicMock(new_codebase=False)
        legacy_raw.get_importlistexclusion.return_value = [{"tvdbId": 42, "title": "HHGTTG"}]

        self.assertEqual([ex.tvdbId for ex in SonarrExclusion.get_all(_fake_arr(paged_raw))], [100, 200])
        self.assertEqual([ex.tvdbId for ex in SonarrExclusion.get_all(_fake_arr(legacy_raw))], [42])
        paged_raw.get_importlistexclusion.assert_not_called()
        legacy_raw.get_importlistexclusion_paged.assert_not_called()

    def test_queue_api_removes_queue_objects_and_ids(self):
        raw = MagicMock()
        api = SimpleNamespace(_raw=raw)
        queue = Queue(_fake_arr(raw), {"id": 7, "title": "Example"})

        SonarrAPI.remove_queue(api, [queue, 8], blocklist=True)

        raw.delete_queue_bulk.assert_called_once_with(
            [7, 8], removeFromClient=True, blocklist=True, skipRedownload=False, changeCategory=False
        )

    def test_episode_monitor_updates_the_object(self):
        raw = MagicMock()
        episode = Episode(_fake_arr(raw), {"id": 4, "title": "Pilot", "monitored": False})

        episode.monitor()

        self.assertTrue(episode.monitored)
        raw.put_episode_monitor.assert_called_once_with([4], True)

    def test_calendar_data_builds_episode_objects_with_related_data(self):
        raw = MagicMock(new_codebase=True)
        raw.get_calendar.return_value = [{
            "id": 5, "title": "Calendar episode", "series": {"id": 4, "title": "Example"},
            "episodeFile": {"id": 9}, "images": [{"coverType": "screenshot", "url": "/image"}]
        }]
        api = SimpleNamespace(_raw=raw)

        calendar = SonarrAPI.calendar(
            api, start="2026-01-01", end="2026-01-31", include_series=True,
            include_episode_file=True, include_episode_images=True
        )

        self.assertEqual(calendar[0].title, "Calendar episode")
        self.assertEqual(calendar[0].series.id, 4)
        self.assertEqual(calendar[0].episodeFile, {"id": 9})
        self.assertEqual(calendar[0].images[0].url, "/image")
        raw.get_calendar.assert_called_once_with(
            start="2026-01-01", end="2026-01-31", unmonitored=False, tags=None,
            includeSeries=True, includeEpisodeFile=True, includeEpisodeImages=True
        )

    def test_calendar_passes_tag_and_enrichment_options(self):
        raw = MagicMock()
        api = SimpleNamespace(_raw=raw, _validate_tags=MagicMock(return_value=[2]))
        raw.get_calendar.return_value = []

        SonarrAPI.calendar(api, tags=2, include_series=True, include_episode_file=True,
                           include_episode_images=True, unmonitored=True)

        raw.get_calendar.assert_called_once_with(
            start=None, end=None, unmonitored=True, tags="2", includeSeries=True,
            includeEpisodeFile=True, includeEpisodeImages=True
        )

    def test_episode_api_methods(self):
        raw = MagicMock()
        raw.get_episode.return_value = [{"id": 4, "title": "Pilot"}]
        api = SimpleNamespace(_raw=raw)

        episodes = SonarrAPI.episodes(api, 12, season_number=1)
        SonarrAPI.monitor_episodes(api, episodes, monitored=False)

        raw.get_episode.assert_called_once_with(seriesId=12, seasonNumber=1)
        raw.put_episode_monitor.assert_called_once_with([4], False)

    def test_raw_feature_endpoints_make_direct_requests(self):
        raw = object.__new__(SonarrRawAPI)
        raw._get = MagicMock()
        raw._put = MagicMock()

        raw.get_calendar("a", "b", tags="1", includeSeries=True, includeEpisodeFile=True,
                         includeEpisodeImages=True)
        raw.get_episode(seriesId=12, seasonNumber=1)
        raw.get_importlistexclusion_paged(page=2, pageSize=5)
        raw.put_episode_monitor([1, 2], False)

        raw._get.assert_any_call(
            "calendar", unmonitored=False, start="a", end="b", tags="1", includeSeries=True,
            includeEpisodeFile=True, includeEpisodeImages=True
        )
        raw._get.assert_any_call("episode", seriesId=12, seasonNumber=1)
        raw._get.assert_any_call("importlistexclusion/paged", page=2, pageSize=5)
        raw._put.assert_called_once_with("episode/monitor", json={"episodeIds": [1, 2], "monitored": False})

    def test_tag_connections_loads_tag_details(self):
        raw = MagicMock()
        raw.get_tag_id.return_value = {
            "id": 3, "label": "connected", "delayProfileIds": [],
            "notificationIds": [10, 11], "restrictionIds": [], "importListIds": []
        }
        tag = Tag(_fake_arr(raw), {"id": 3, "label": "connected"})

        self.assertEqual(tag.connections, 2)
        raw.get_tag_id.assert_called_once_with(3, detail=True)





