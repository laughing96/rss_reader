from django.db import models

class Story(models.Model):
    hn_id = models.IntegerField(unique=True, db_index=True)
    title = models.CharField(max_length=500)
    url = models.URLField(max_length=1000, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    by = models.CharField(max_length=100)
    score = models.IntegerField(default=0)
    time = models.DateTimeField()
    descendants = models.IntegerField(default=0)
    type = models.CharField(max_length=20, default="story")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'stories'
        indexes = [
            models.Index(fields=['hn_id']),
        ]

class RSSFeed(models.Model):
    title = models.CharField(max_length=500)
    url = models.URLField(max_length=1000)
    feed_url = models.URLField(max_length=1000, unique=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_fetched = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'rss_feeds'

class RSSItem(models.Model):
    feed = models.CharField(max_length=500)
    title = models.CharField(max_length=500)
    link = models.URLField(max_length=1000)
    description = models.TextField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rss_items'
        unique_together = ['feed', 'link']
