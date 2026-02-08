import os
import json
import httpx
import feedparser
from datetime import datetime
from typing import List, Dict, Any
from django.core.cache import cache
from .models import Story, RSSFeed, RSSItem

HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

CACHE_TTL = 300  # 5 minutes

def fetch_hn_top_stories(limit: int = 30) -> List[Story]:
    """Fetch Hacker News top stories"""
    cache_key = f"hn_top_stories_{limit}"
    cached = cache.get(cache_key)
    
    if cached:
        story_ids = json.loads(cached)
        return Story.objects.filter(hn_id__in=story_ids)
    
    response = httpx.get(HN_TOP_STORIES_URL)
    story_ids = response.json()[:limit]
    
    stories = []
    stories_data = []
    
    for story_id in story_ids:
        story = Story.objects.filter(hn_id=story_id).first()
        
        if not story:
            item_response = httpx.get(HN_ITEM_URL.format(story_id))
            item_data = item_response.json()
            
            if item_data and item_data.get('type') == 'story':
                story = Story.objects.create(
                    hn_id=item_data['id'],
                    title=item_data.get('title', ''),
                    url=item_data.get('url'),
                    text=item_data.get('text'),
                    by=item_data.get('by', 'unknown'),
                    score=item_data.get('score', 0),
                    time=datetime.fromtimestamp(item_data.get('time', 0)),
                    descendants=item_data.get('descendants', 0),
                    type=item_data.get('type', 'story')
                )
        
        if story:
            stories.append(story)
            stories_data.append(story.hn_id)
    
    cache.set(cache_key, json.dumps(stories_data), CACHE_TTL)
    return stories

def fetch_rss_feed(feed_id: int) -> List[RSSItem]:
    """Fetch RSS feed content"""
    feed = RSSFeed.objects.filter(id=feed_id).first()
    if not feed:
        return []
    
    parsed = feedparser.parse(feed.feed_url)
    items = []
    
    for entry in parsed.entries[:30]:
        existing = RSSItem.objects.filter(feed=feed, link=entry.link).first()
        
        if not existing:
            published = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6])
            
            item = RSSItem.objects.create(
                feed=feed,
                title=entry.get('title', 'Untitled'),
                link=entry.link,
                description=entry.get('summary', entry.get('description', '')),
                published_at=published
            )
            items.append(item)
        else:
            items.append(existing)
    
    feed.last_fetched = datetime.utcnow()
    feed.save()
    
    return items

def fetch_all_rss_items() -> List[Dict[str, Any]]:
    """Fetch all RSS items"""
    cache_key = "rss_all_items"
    cached = cache.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    feeds = RSSFeed.objects.all()
    all_items = []
    
    for feed in feeds:
        items = fetch_rss_feed(feed.id)
        for item in items:
            all_items.append({
                'id': item.id,
                'feed_id': item.feed_id,
                'title': item.title,
                'link': item.link,
                'description': item.description,
                'published_at': item.published_at.isoformat() if item.published_at else None,
                'created_at': item.created_at.isoformat()
            })
    
    cache.set(cache_key, json.dumps(all_items), CACHE_TTL)
    return all_items

def add_default_feeds():
    """Add default RSS feeds"""
    default_feeds = [
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
