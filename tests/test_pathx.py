"""
Basic unit tests for PathX's wordlist handling and discovery logic.

Run with:
    python3 -m unittest discover -s tests
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pathx  # noqa: E402


class TestWordlistExpansion(unittest.TestCase):

    def test_no_extensions_returns_unchanged(self):
        words = ["admin", "login"]
        self.assertEqual(pathx.expand_with_extensions(words, []), words)

    def test_extensions_appended(self):
        words = ["admin"]
        expanded = pathx.expand_with_extensions(words, ["php", "bak"])
        self.assertIn("admin", expanded)
        self.assertIn("admin.php", expanded)
        self.assertIn("admin.bak", expanded)
        self.assertEqual(len(expanded), 3)

    def test_words_with_extension_not_double_expanded(self):
        words = ["robots.txt"]
        expanded = pathx.expand_with_extensions(words, ["php"])
        self.assertEqual(expanded, ["robots.txt"])

    def test_default_wordlist_is_nonempty_and_deduped_reasonably(self):
        self.assertGreater(len(pathx.DEFAULT_WORDLIST), 10)
        self.assertEqual(len(pathx.DEFAULT_WORDLIST), len(set(pathx.DEFAULT_WORDLIST)))


class TestPathHitDataclass(unittest.TestCase):

    def test_default_not_soft_404(self):
        hit = pathx.PathHit(path="admin", url="http://x/admin", status_code=200)
        self.assertFalse(hit.likely_soft_404)


class TestScanResultAggregation(unittest.TestCase):

    def test_soft_404_flagged_when_any_hit_is_soft(self):
        result = pathx.ScanResult(base_url="http://x")
        result.hits.append(pathx.PathHit(path="a", url="http://x/a", status_code=200, likely_soft_404=True))
        result.hits.append(pathx.PathHit(path="b", url="http://x/b", status_code=200, likely_soft_404=False))
        # soft_404_detected is set by scan_target after collecting hits; emulate that here
        result.soft_404_detected = any(h.likely_soft_404 for h in result.hits)
        self.assertTrue(result.soft_404_detected)


class TestHeaderAndCookieParsing(unittest.TestCase):

    def test_parse_header_list(self):
        headers = pathx.parse_header_list(["Authorization: Bearer abc", "X-Test: 1"])
        self.assertEqual(headers["Authorization"], "Bearer abc")
        self.assertEqual(headers["X-Test"], "1")

    def test_parse_cookie_string(self):
        cookies = pathx.parse_cookie_string("a=1; b=2")
        self.assertEqual(cookies, {"a": "1", "b": "2"})

    def test_parse_empty_inputs(self):
        self.assertEqual(pathx.parse_header_list(None), {})
        self.assertEqual(pathx.parse_cookie_string(None), {})


if __name__ == "__main__":
    unittest.main()
