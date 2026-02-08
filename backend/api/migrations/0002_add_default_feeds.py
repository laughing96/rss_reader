from django.db import migrations


def add_default_feeds(apps, schema_editor):
    """Add default RSS feeds including Dev.to"""
    RSSFeed = apps.get_model('api', 'RSSFeed')
    
    default_feeds = [
        {
            "title": "Dev.to",
            "url": "https://dev.to",
            "feed_url": "https://dev.to/feed",
            "description": "Developer Community and Programming Articles"
        },
        {
            "title": "TechCrunch",
            "url": "https://techcrunch.com",
            "feed_url": "https://techcrunch.com/feed/",
            "description": "Startup and Technology News"
        },
        {
            "title": "The Verge",
            "url": "https://www.theverge.com",
            "feed_url": "https://www.theverge.com/rss/index.xml",
            "description": "Technology and Culture"
        },
        {
            "title": "Ars Technica",
            "url": "https://arstechnica.com",
            "feed_url": "https://feeds.arstechnica.com/arstechnica/index",
            "description": "Technology and Science News"
        }
    ]
    
    for feed_data in default_feeds:
        if not RSSFeed.objects.filter(feed_url=feed_data["feed_url"]).exists():
            RSSFeed.objects.create(**feed_data)


def remove_default_feeds(apps, schema_editor):
    """Remove default RSS feeds"""
    RSSFeed = apps.get_model('api', 'RSSFeed')
    
    default_feed_urls = [
        "https://dev.to/feed",
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
        "https://feeds.arstechnica.com/arstechnica/index"
    ]
    
    RSSFeed.objects.filter(feed_url__in=default_feed_urls).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_default_feeds, remove_default_feeds),
    ]
