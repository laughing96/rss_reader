import json
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.utils import timezone

from api.models import Story, RSSFeed, RSSItem
from api.services import (
    fetch_hn_top_stories, fetch_rss_feed, fetch_all_rss_items,
    parse_opml_file, import_opml_feeds, add_default_feeds
)


class FetchHNTopStoriesTest(TestCase):
    @patch('api.services.cache')
    @patch('api.services.httpx.get')
    def test_fetch_hn_stories_from_cache(self, mock_get, mock_cache):
        mock_cache.get.return_value = json.dumps([1, 2, 3])
        mock_get.return_value = MagicMock()

        Story.objects.create(hn_id=1, title="Story 1", by="user", time=timezone.now())
        Story.objects.create(hn_id=2, title="Story 2", by="user", time=timezone.now())
        Story.objects.create(hn_id=3, title="Story 3", by="user", time=timezone.now())

        stories = fetch_hn_top_stories(limit=3)
        self.assertEqual(len(stories), 3)
        mock_cache.get.assert_called_once()

    @patch('api.services.cache')
    @patch('api.services.httpx.get')
    def test_fetch_hn_stories_from_api(self, mock_get, mock_cache):
        mock_cache.get.return_value = None

        mock_response_1 = MagicMock()
        mock_response_1.json.return_value = [123]

        mock_response_2 = MagicMock()
        mock_response_2.json.return_value = {
            "id": 123,
            "title": "API Story",
            "url": "https://example.com",
            "by": "user",
            "score": 10,
            "time": 1700000000,
            "descendants": 5,
            "type": "story"
        }

        mock_get.side_effect = [mock_response_1, mock_response_2]

        stories = fetch_hn_top_stories(limit=1)
        self.assertEqual(len(stories), 1)
        self.assertEqual(Story.objects.count(), 1)
        mock_cache.set.assert_called_once()

    @patch('api.services.cache')
    @patch('api.services.httpx.get')
    def test_fetch_hn_stories_existing(self, mock_get, mock_cache):
        mock_cache.get.return_value = None

        mock_response = MagicMock()
        mock_response.json.return_value = [999]
        mock_get.return_value = mock_response

        Story.objects.create(
            hn_id=999,
            title="Existing Story",
            by="user",
            time=timezone.now()
        )

        stories = fetch_hn_top_stories(limit=1)
        self.assertEqual(len(stories), 1)
        self.assertEqual(stories[0].title, "Existing Story")
        self.assertEqual(Story.objects.count(), 1)


class FetchRSSFeedTest(TestCase):
    @patch('api.services.feedparser.parse')
    def test_fetch_rss_feed_creates_items(self, mock_parse):
        feed = RSSFeed.objects.create(
            title="Test Feed",
            url="https://example.com",
            feed_url="https://example.com/feed.xml"
        )

        mock_entry = MagicMock()
        mock_entry.link = "https://example.com/item1"
        mock_entry.title = "Test Item"
        mock_entry.get.return_value = "Description"
        mock_entry.published_parsed = (2024, 1, 1, 12, 0, 0)

        mock_parse.return_value = MagicMock(entries=[mock_entry])

        items = fetch_rss_feed(feed.id)
        self.assertEqual(len(items), 1)
        self.assertEqual(RSSItem.objects.count(), 1)
        feed.refresh_from_db()
        self.assertIsNotNone(feed.last_fetched)

    @patch('api.services.feedparser.parse')
    def test_fetch_rss_feed_existing_items(self, mock_parse):
        feed = RSSFeed.objects.create(
            title="Test Feed",
            url="https://example.com",
            feed_url="https://example.com/feed.xml"
        )

        RSSItem.objects.create(
            feed=feed.id,
            title="Existing Item",
            link="https://example.com/item1"
        )

        mock_entry = MagicMock()
        mock_entry.link = "https://example.com/item1"
        mock_entry.title = "New Title"
        mock_entry.get.return_value = "Description"
        mock_entry.published_parsed = None

        mock_parse.return_value = MagicMock(entries=[mock_entry])

        items = fetch_rss_feed(feed.id)
        self.assertEqual(len(items), 1)
        self.assertEqual(RSSItem.objects.count(), 1)
        items[0].refresh_from_db()
        self.assertEqual(items[0].title, "Existing Item")

    def test_fetch_rss_feed_invalid_id(self):
        items = fetch_rss_feed(99999)
        self.assertEqual(len(items), 0)


class FetchAllRSSItemsTest(TestCase):
    @patch('api.services.cache')
    @patch('api.services.fetch_rss_feed')
    def test_fetch_all_rss_items_from_cache(self, mock_fetch, mock_cache):
        mock_cache.get.return_value = json.dumps([{"id": 1, "title": "Cached"}])

        items = fetch_all_rss_items()
        self.assertEqual(len(items), 1)
        mock_fetch.assert_not_called()

    @patch('api.services.cache')
    @patch('api.services.fetch_rss_feed')
    def test_fetch_all_rss_items(self, mock_fetch, mock_cache):
        mock_cache.get.return_value = None

        feed = RSSFeed.objects.create(
            title="Feed",
            url="https://example.com",
            feed_url="https://example.com/feed.xml"
        )

        item = RSSItem.objects.create(
            feed=feed.id,
            title="Test Item",
            link="https://example.com/item"
        )

        mock_fetch.return_value = [item]

        items = fetch_all_rss_items()
        self.assertEqual(len(items), 5)
        mock_cache.set.assert_called_once()


class ParseOPMLFileTest(TestCase):
    def test_parse_valid_opml(self):
        opml_content = """<?xml version="1.0" encoding="UTF-8"?>
<opml version="2.0">
  <body>
    <outline text="Feed 1" xmlUrl="https://example.com/feed1.xml" htmlUrl="https://example.com"/>
  </body>
</opml>"""

        feeds, errors = parse_opml_file(opml_content)
        self.assertEqual(len(feeds), 1)
        self.assertEqual(feeds[0]['feed_url'], "https://example.com/feed1.xml")
        self.assertEqual(len(errors), 0)

    def test_parse_opml_with_nested_outlines(self):
        opml_content = """<?xml version="1.0" encoding="UTF-8"?>
<opml version="2.0">
  <body>
    <outline text="Folder" xmlUrl="">
      <outline text="Nested Feed" xmlUrl="https://example.com/nested.xml"/>
    </outline>
  </body>
</opml>"""

        feeds, errors = parse_opml_file(opml_content)
        self.assertIn(len(feeds), [1, 2])
        self.assertTrue(any(f['feed_url'] == "https://example.com/nested.xml" for f in feeds))

    def test_parse_invalid_xml(self):
        opml_content = "<invalid>xml"
        feeds, errors = parse_opml_file(opml_content)
        self.assertEqual(len(feeds), 0)
        self.assertTrue(len(errors) > 0)

    def test_parse_empty_opml(self):
        opml_content = """<?xml version="1.0" encoding="UTF-8"?>
<opml version="2.0">
  <body>
  </body>
</opml>"""

        feeds, errors = parse_opml_file(opml_content)
        self.assertEqual(len(feeds), 0)


class ImportOPMLFeedsTest(TestCase):
    @patch('api.services.fetch_rss_feed')
    def test_import_new_feeds(self, mock_fetch):
        mock_fetch.return_value = []
        opml_content = """<?xml version="1.0" encoding="UTF-8"?>
<opml version="2.0">
  <body>
    <outline text="Feed" xmlUrl="https://example.com/feed.xml"/>
  </body>
</opml>"""

        result = import_opml_feeds(opml_content)
        self.assertEqual(len(result['added']), 1)
        self.assertEqual(len(result['skipped']), 0)
        self.assertEqual(len(result['failed']), 0)

    @patch('api.services.fetch_rss_feed')
    def test_import_skip_existing_feeds(self, mock_fetch):
        mock_fetch.return_value = []
        RSSFeed.objects.create(
            title="Existing",
            url="https://example.com",
            feed_url="https://example.com/feed.xml"
        )

        opml_content = """<?xml version="1.0" encoding="UTF-8"?>
<opml version="2.0">
  <body>
    <outline text="Feed" xmlUrl="https://example.com/feed.xml"/>
  </body>
</opml>"""

        result = import_opml_feeds(opml_content)
        self.assertEqual(len(result['added']), 0)
        self.assertEqual(len(result['skipped']), 1)


class AddDefaultFeedsTest(TestCase):
    @patch('api.services.fetch_rss_feed')
    def test_add_default_feeds(self, mock_fetch):
        mock_fetch.return_value = []
        add_default_feeds()
        self.assertGreater(RSSFeed.objects.count(), 0)

    @patch('api.services.fetch_rss_feed')
    def test_add_default_feeds_no_duplicates(self, mock_fetch):
        mock_fetch.return_value = []
        add_default_feeds()
        count = RSSFeed.objects.count()
        add_default_feeds()
        self.assertEqual(RSSFeed.objects.count(), count)
