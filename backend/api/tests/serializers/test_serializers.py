from django.test import TestCase
from django.utils import timezone

from api.models import Story, Folder, RSSFeed, RSSItem
from api.serializers import (
    StorySerializer, FolderSerializer, RSSFeedSerializer, RSSItemSerializer
)


class StorySerializerTest(TestCase):
    def test_story_serializer(self):
        story = Story.objects.create(
            hn_id=123,
            title="Test",
            by="user",
            time=timezone.now()
        )
        serializer = StorySerializer(story)
        self.assertEqual(serializer.data['title'], "Test")


class FolderSerializerTest(TestCase):
    def test_folder_serializer(self):
        folder = Folder.objects.create(name="Test Folder")
        serializer = FolderSerializer(folder)
        self.assertEqual(serializer.data['name'], "Test Folder")


class RSSFeedSerializerTest(TestCase):
    def test_rss_feed_serializer(self):
        feed = RSSFeed.objects.create(
            title="Test",
            url="https://example.com",
            feed_url="https://example.com/feed.xml"
        )
        serializer = RSSFeedSerializer(feed)
        self.assertEqual(serializer.data['title'], "Test")


class RSSItemSerializerTest(TestCase):
    def test_rss_item_serializer(self):
        feed = RSSFeed.objects.create(
            title="Test",
            url="https://example.com",
            feed_url="https://example.com/feed.xml"
        )
        item = RSSItem.objects.create(
            feed=feed.id,
            title="Item",
            link="https://example.com/item"
        )
        serializer = RSSItemSerializer(item)
        self.assertEqual(serializer.data['title'], "Item")
