from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.utils import timezone

from api.models import Story, Folder, RSSFeed, RSSItem


class RootViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_root_endpoint(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Hacker News + RSS Reader API')

    def test_health_check(self):
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'healthy')


class HNStoriesViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    @patch('api.services.httpx.get')
    def test_get_hn_stories(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [12345]
        mock_get.return_value = mock_response

        Story.objects.create(
            hn_id=12345,
            title="HN Story",
            by="user",
            time=timezone.now()
        )

        response = self.client.get('/api/hn/stories')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], "HN Story")

    @patch('api.services.httpx.get')
    def test_get_hn_stories_with_limit(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [1, 2, 3]
        mock_get.return_value = mock_response

        Story.objects.create(hn_id=1, title="Story 1", by="user1", time=timezone.now())
        Story.objects.create(hn_id=2, title="Story 2", by="user2", time=timezone.now())
        Story.objects.create(hn_id=3, title="Story 3", by="user3", time=timezone.now())

        response = self.client.get('/api/hn/stories?limit=2')
        self.assertEqual(response.status_code, 200)


class FoldersViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_folders(self):
        Folder.objects.create(name="Folder 1")
        Folder.objects.create(name="Folder 2")

        response = self.client.get('/api/rss/folders')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)

    def test_get_folders_with_parent_filter(self):
        parent = Folder.objects.create(name="Parent")
        Folder.objects.create(name="Child", parent=parent)
        Folder.objects.create(name="Orphan")

        response = self.client.get(f'/api/rss/folders?folder={parent.id}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('folder', data)
        self.assertIn('feeds', data)

    def test_create_folder(self):
        response = self.client.post('/api/rss/folders', {'name': 'New Folder'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Folder.objects.count(), 1)

    def test_create_duplicate_folder_fails(self):
        Folder.objects.create(name="Test", parent_id=None)
        response = self.client.post('/api/rss/folders', {'name': 'Test'})
        self.assertEqual(response.status_code, 400)

    def test_create_nested_folder(self):
        parent = Folder.objects.create(name="Parent")
        response = self.client.post('/api/rss/folders', {
            'name': 'Child',
            'parent': parent.id
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Folder.objects.get(name="Child").parent, parent)


class FolderDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_folder_detail(self):
        folder = Folder.objects.create(name="Test Folder")
        response = self.client.get(f'/api/rss/folders/{folder.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], "Test Folder")

    def test_get_nonexistent_folder(self):
        response = self.client.get('/api/rss/folders/99999')
        self.assertEqual(response.status_code, 404)

    def test_update_folder(self):
        folder = Folder.objects.create(name="Old Name")
        response = self.client.put(
            f'/api/rss/folders/{folder.id}',
            {'name': 'New Name'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        folder.refresh_from_db()
        self.assertEqual(folder.name, "New Name")

    def test_delete_folder(self):
        folder = Folder.objects.create(name="To Delete")
        feed = RSSFeed.objects.create(
            title="Feed",
            url="https://example.com",
            feed_url="https://example.com/feed.xml",
            folder=folder
        )
        response = self.client.delete(f'/api/rss/folders/{folder.id}')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Folder.objects.filter(id=folder.id).exists())
        feed.refresh_from_db()
        self.assertIsNone(feed.folder)


class RSSFeedsViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_feeds(self):
        RSSFeed.objects.create(
            title="Feed 1",
            url="https://example1.com",
            feed_url="https://example1.com/feed.xml"
        )

        response = self.client.get('/api/rss/feeds')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 5)  # 4 default + 1 created

    @patch('api.views.fetch_rss_feed')
    def test_create_feed(self, mock_fetch):
        mock_fetch.return_value = []
        response = self.client.post('/api/rss/feeds', {
            'title': 'New Feed',
            'url': 'https://example.com',
            'feed_url': 'https://example.com/feed.xml'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(RSSFeed.objects.count(), 5)  # 4 default + 1

    def test_create_duplicate_feed_fails(self):
        RSSFeed.objects.create(
            title="Feed",
            url="https://example.com",
            feed_url="https://example.com/feed.xml"
        )
        response = self.client.post('/api/rss/feeds', {
            'title': 'Another',
            'url': 'https://example2.com',
            'feed_url': 'https://example.com/feed.xml'
        })
        self.assertEqual(response.status_code, 400)


class RSSFeedDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_delete_feed(self):
        feed = RSSFeed.objects.create(
            title="Feed",
            url="https://example.com",
            feed_url="https://example.com/feed.xml"
        )
        RSSItem.objects.create(feed=feed.id, title="Item", link="https://example.com/1")

        response = self.client.delete(f'/api/rss/feeds/{feed.id}')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(RSSFeed.objects.filter(id=feed.id).exists())
        self.assertEqual(RSSItem.objects.filter(feed=feed.id).count(), 0)


class RSSItemsViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    @patch('api.views.fetch_rss_feed')
    def test_get_items_by_feed(self, mock_fetch):
        mock_fetch.return_value = []
        feed = RSSFeed.objects.create(
            title="Feed",
            url="https://example.com",
            feed_url="https://example.com/feed.xml"
        )
        RSSItem.objects.create(feed=feed.id, title="Item 1", link="https://example.com/1")

        response = self.client.get(f'/api/rss/items?feed={feed.id}')
        self.assertEqual(response.status_code, 200)

    @patch('api.views.fetch_all_rss_items')
    def test_get_all_items(self, mock_fetch):
        mock_fetch.return_value = []
        response = self.client.get('/api/rss/items')
        self.assertEqual(response.status_code, 200)


class CombinedItemsViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    @patch('api.views.fetch_hn_top_stories')
    @patch('api.views.fetch_all_rss_items')
    def test_get_combined_items(self, mock_rss, mock_hn):
        story = Story.objects.create(
            hn_id=1,
            title="HN Story",
            by="user",
            time=timezone.now()
        )
        mock_hn.return_value = [story]
        mock_rss.return_value = []

        response = self.client.get('/api/combined')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['type'], 'hn')


class MoveFeedToFolderViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_move_feed_to_folder(self):
        folder = Folder.objects.create(name="Folder")
        feed = RSSFeed.objects.create(
            title="Feed",
            url="https://example.com",
            feed_url="https://example.com/feed.xml"
        )

        response = self.client.post(
            f'/api/rss/feeds/{feed.id}/move',
            {'folder': folder.id},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        feed.refresh_from_db()
        self.assertEqual(feed.folder, folder)

    def test_move_feed_from_folder(self):
        folder = Folder.objects.create(name="Folder")
        feed = RSSFeed.objects.create(
            title="Feed",
            url="https://example.com",
            feed_url="https://example.com/feed.xml",
            folder=folder
        )

        response = self.client.post(
            f'/api/rss/feeds/{feed.id}/move',
            {'folder': None},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        feed.refresh_from_db()
        self.assertIsNone(feed.folder)
