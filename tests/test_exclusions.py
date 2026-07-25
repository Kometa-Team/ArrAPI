"""Unit tests for the paginated Import List Exclusion loading logic.

These tests intentionally avoid touching the network — the whole point of
`RadarrExclusion.get_all` / `SonarrExclusion.get_all` is the pagination glue
around the raw HTTP calls, so we mock those out and exercise the glue.
"""

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from arrapi.objs.simple import RadarrExclusion, SonarrExclusion, _paginate


def _fake_arr(raw):
    """Build the minimum surface `SimpleObj` needs: ``arr._raw`` and ``arr._raw``.

    ``BaseObj.__init__`` does ``self._raw = arr._raw`` and then calls ``_load(data)``,
    so we only need ``._raw`` on the fake arr. Both raw stubs must expose whatever
    method the ``get_all`` classmethod reaches for.
    """
    return SimpleNamespace(_raw=raw)


class PaginateHelperTests(unittest.TestCase):
    def test_stops_when_totalRecords_reached(self):
        pages = [
            {"records": [{"tmdbId": 1}, {"tmdbId": 2}], "totalRecords": 3},
            {"records": [{"tmdbId": 3}], "totalRecords": 3},
        ]
        getter = MagicMock(side_effect=pages)
        result = list(_paginate(arr=None, paged_getter=getter, page_size=2))
        self.assertEqual([r["tmdbId"] for r in result], [1, 2, 3])
        self.assertEqual(getter.call_count, 2)
        getter.assert_any_call(page=1, pageSize=2)
        getter.assert_any_call(page=2, pageSize=2)

    def test_stops_on_short_page_when_totalRecords_missing(self):
        pages = [
            {"records": [{"tmdbId": 1}, {"tmdbId": 2}]},
            {"records": [{"tmdbId": 3}]},  # short page -> stop
        ]
        getter = MagicMock(side_effect=pages)
        result = list(_paginate(arr=None, paged_getter=getter, page_size=2))
        self.assertEqual([r["tmdbId"] for r in result], [1, 2, 3])
        self.assertEqual(getter.call_count, 2)

    def test_handles_empty_first_page(self):
        getter = MagicMock(return_value={"records": [], "totalRecords": 0})
        self.assertEqual(list(_paginate(arr=None, paged_getter=getter, page_size=10)), [])
        self.assertEqual(getter.call_count, 1)

    def test_handles_none_response(self):
        # Some Arr error paths return None from _get.
        getter = MagicMock(return_value=None)
        self.assertEqual(list(_paginate(arr=None, paged_getter=getter, page_size=10)), [])
        self.assertEqual(getter.call_count, 1)


class RadarrExclusionGetAllTests(unittest.TestCase):
    def test_new_codebase_uses_paged_endpoint(self):
        raw = MagicMock()
        raw.new_codebase = True
        raw.get_exclusions_paged.side_effect = [
            {"records": [
                {"tmdbId": 11, "movieTitle": "Star Wars", "movieYear": 1977},
                {"tmdbId": 1891, "movieTitle": "The Empire Strikes Back", "movieYear": 1980},
            ], "totalRecords": 2},
        ]
        exclusions = RadarrExclusion.get_all(_fake_arr(raw))
        self.assertEqual([e.tmdbId for e in exclusions], [11, 1891])
        self.assertEqual([e.title for e in exclusions], ["Star Wars", "The Empire Strikes Back"])
        raw.get_exclusions.assert_not_called()
        raw.get_exclusions_paged.assert_called_once_with(page=1, pageSize=250)

    def test_legacy_codebase_uses_flat_endpoint(self):
        raw = MagicMock()
        raw.new_codebase = False
        raw.get_exclusions.return_value = [
            {"tmdbId": 1, "movieTitle": "Old", "movieYear": 1999},
        ]
        exclusions = RadarrExclusion.get_all(_fake_arr(raw))
        self.assertEqual([e.tmdbId for e in exclusions], [1])
        raw.get_exclusions_paged.assert_not_called()
        raw.get_exclusions.assert_called_once_with()


class SonarrExclusionGetAllTests(unittest.TestCase):
    def test_new_codebase_uses_paged_endpoint(self):
        raw = MagicMock()
        raw.new_codebase = True
        raw.get_importlistexclusion_paged.side_effect = [
            {"records": [
                {"tvdbId": 100, "title": "Breaking Bad"},
                {"tvdbId": 200, "title": "The Wire"},
            ], "totalRecords": 3},
            {"records": [
                {"tvdbId": 300, "title": "Firefly"},
            ], "totalRecords": 3},
        ]
        exclusions = SonarrExclusion.get_all(_fake_arr(raw))
        self.assertEqual([e.tvdbId for e in exclusions], [100, 200, 300])
        raw.get_importlistexclusion.assert_not_called()
        self.assertEqual(raw.get_importlistexclusion_paged.call_count, 2)

    def test_legacy_codebase_uses_flat_endpoint(self):
        raw = MagicMock()
        raw.new_codebase = False
        raw.get_importlistexclusion.return_value = [
            {"tvdbId": 42, "title": "HHGTTG"},
        ]
        exclusions = SonarrExclusion.get_all(_fake_arr(raw))
        self.assertEqual([e.tvdbId for e in exclusions], [42])
        raw.get_importlistexclusion_paged.assert_not_called()
        raw.get_importlistexclusion.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
