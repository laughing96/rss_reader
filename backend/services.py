import os
import json
import httpx
import redis
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from database import Story, RSSFeed, RSSItem
import feedparser

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

CACHE_TTL = 300  # 5 minutes

async def fetch_hn_top_stories(db: Session, limit: int = 30) -> List[Story]:
    """获取 Hacker News 热门文章"""
    cache_key = f"hn_top_stories_{limit}"
    cached = redis_client.get(cache_key)
    
    if cached:
        stories_data = json.loads(cached)
        return [Story(**story) for story in stories_data]
    
    async with httpx.AsyncClient() as client:
        response = await client.get(HN_TOP_STORIES_URL)
        story_ids = response.json()[:limit]
        
        stories = []
        stories_data = []
        
        for story_id in story_ids:
            # 先检查数据库
            story = db.query(Story).filter(Story.hn_id == story_id).first()
            
            if not story:
                # 从 HN API 获取
                item_response = await client.get(HN_ITEM_URL.format(story_id))
                item_data = item_response.json()
                
                if item_data and item_data.get('type') == 'story':
                    story = Story(
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
                    db.add(story)
                    db.commit()
                    db.refresh(story)
            
            if story:
                stories.append(story)
                stories_data.append({
                    'id': story.id,
                    'hn_id': story.hn_id,
                    'title': story.title,
                    'url': story.url,
                    'text': story.text,
                    'by': story.by,
                    'score': story.score,
                    'time': story.time.isoformat(),
                    'descendants': story.descendants,
                    'type': story.type
                })
        
        # 缓存到 Redis
        redis_client.setex(cache_key, CACHE_TTL, json.dumps(stories_data))
        
        return stories

async def fetch_rss_feed(db: Session, feed_id: int) -> List[RSSItem]:
    """获取 RSS feed 内容"""
    feed = db.query(RSSFeed).filter(RSSFeed.id == feed_id).first()
    if not feed:
        return []
    
    parsed = feedparser.parse(feed.feed_url)
    items = []
    
    for entry in parsed.entries[:30]:
        # 检查是否已存在
        existing = db.query(RSSItem).filter(
            RSSItem.feed_id == feed_id,
            RSSItem.link == entry.link
        ).first()
        
        if not existing:
            published = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6])
            
            item = RSSItem(
                feed_id=feed_id,
                title=entry.get('title', 'Untitled'),
                link=entry.link,
                description=entry.get('summary', entry.get('description', '')),
                published_at=published
            )
            db.add(item)
            items.append(item)
        else:
            items.append(existing)
    
    feed.last_fetched = datetime.utcnow()
    db.commit()
    
    return items

async def fetch_all_rss_items(db: Session) -> List[RSSItem]:
    """获取所有 RSS items"""
    cache_key = "rss_all_items"
    cached = redis_client.get(cache_key)
    
    if cached:
        items_data = json.loads(cached)
        return items_data
    
    feeds = db.query(RSSFeed).all()
    all_items = []
    
    for feed in feeds:
        items = await fetch_rss_feed(db, feed.id)
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
    
    # 缓存 5 分钟
    redis_client.setex(cache_key, CACHE_TTL, json.dumps(all_items))
    
    return all_items

def add_default_feeds(db: Session):
    """添加默认 RSS feeds"""
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
        existing = db.query(RSSFeed).filter(RSSFeed.feed_url == feed_data["feed_url"]).first()
        if not existing:
            feed = RSSFeed(**feed_data)
            db.add(feed)
    
    db.commit()
