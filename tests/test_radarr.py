import os, unittest

from arrapi import RadarrAPI, NotFound, Exists
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





