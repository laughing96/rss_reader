from django.test import TestCase
from django.utils import timezone

from api.models import Story, Folder, RSSFeed, RSSItem


class StoryModelTest(TestCase):
    def test_create_story(self):
        story = Story.objects.create(
            hn_id=12345,
            title="Test Story",
            url="https://example.com",
            text="Test content",
            by="testuser",
            score=100,
            time=timezone.now(),
            descendants=50
        )
        self.assertEqual(story.title, "Test Story")
        self.assertEqual(story.hn_id, 12345)
        self.assertEqual(story.score, 100)

    def test_story_unique_hn_id(self):
        Story.objects.create(hn_id=1, title="Story 1", by="user1", time=timezone.now())
        with self.assertRaises(Exception):
            Story.objects.create(hn_id=1, title="Story 2", by="user2", time=timezone.now())


class FolderModelTest(TestCase):
    def test_create_folder(self):
        folder = Folder.objects.create(name="Tech")
        self.assertEqual(str(folder), "Tech")

    def test_create_nested_folder(self):
        parent = Folder.objects.create(name="Parent")
        child = Folder.objects.create(name="Child", parent=parent)
        self.assertEqual(child.parent, parent)
        self.assertEqual(parent.children.count(), 1)


class RSSFeedModelTest(TestCase):
    def test_create_feed(self):
        feed = RSSFeed.objects.create(
            title="Test Feed",
            url="https://example.com",
            feed_url="https://example.com/feed.xml"
        )
        self.assertEqual(feed.title, "Test Feed")

    def test_feed_unique_feed_url(self):
        RSSFeed.objects.create(
            title="Feed 1",
            url="https://example.com",
            feed_url="https://example.com/feed.xml"
        )
        with self.assertRaises(Exception):
            RSSFeed.objects.create(
                title="Feed 2",
                url="https://example2.com",
                feed_url="https://example.com/feed.xml"
            )

    def test_feed_with_folder(self):
        folder = Folder.objects.create(name="News")
        feed = RSSFeed.objects.create(
            title="Test Feed",
            url="https://example.com",
            feed_url="https://example.com/feed.xml",
            folder=folder
        )
        self.assertEqual(feed.folder, folder)


class RSSItemModelTest(TestCase):
    def test_create_item(self):
        feed = RSSFeed.objects.create(
            title="Test Feed",
            url="https://example.com",
            feed_url="https://example.com/feed.xml"
        )
        item = RSSItem.objects.create(
            feed=feed.id,
            title="Test Item",
            link="https://example.com/item1",
            description="Test description"
        )
        self.assertEqual(item.title, "Test Item")
        self.assertEqual(item.feed, feed.id)

    def test_item_unique_together(self):
        feed = RSSFeed.objects.create(
            title="Test Feed",
            url="https://example.com",
            feed_url="https://example.com/feed.xml"
        )
        RSSItem.objects.create(
            feed=feed.id,
            title="Item 1",
            link="https://example.com/item1"
        )
        with self.assertRaises(Exception):
            RSSItem.objects.create(
                feed=feed.id,
                title="Item 2",
                link="https://example.com/item1"
            )
