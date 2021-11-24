import os, unittest

from arrapi import SonarrAPI, NotFound, Exists
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





