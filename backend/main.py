from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from contextlib import asynccontextmanager

from database import init_db, get_db, SessionLocal
from schemas import (
    StoryResponse, RSSFeedCreate, RSSFeedResponse, 
    RSSItemResponse, CombinedItem
)
from services import (
    fetch_hn_top_stories, fetch_all_rss_items, 
    fetch_rss_feed, add_default_feeds
)
from database import RSSFeed, RSSItem

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    init_db()
    
    # 添加默认 feeds
    db = SessionLocal()
    try:
        add_default_feeds(db)
    finally:
        db.close()
    
    yield
    # 关闭时清理

app = FastAPI(
    title="Hacker News + RSS Reader API",
    description="A combined reader for Hacker News and RSS feeds",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Hacker News + RSS Reader API",
        "docs": "/docs",
        "endpoints": {
            "hn_stories": "/api/hn/stories",
            "rss_feeds": "/api/rss/feeds",
            "rss_items": "/api/rss/items",
            "combined": "/api/combined"
        }
    }

@app.get("/api/hn/stories", response_model=List[StoryResponse])
async def get_hn_stories(limit: int = 30, db: Session = Depends(get_db)):
    """获取 Hacker News 热门文章"""
    stories = await fetch_hn_top_stories(db, limit=limit)
    return stories

@app.get("/api/rss/feeds", response_model=List[RSSFeedResponse])
async def get_rss_feeds(db: Session = Depends(get_db)):
    """获取所有 RSS feeds"""
    feeds = db.query(RSSFeed).all()
    return feeds

@app.post("/api/rss/feeds", response_model=RSSFeedResponse)
async def create_rss_feed(feed: RSSFeedCreate, db: Session = Depends(get_db)):
    """添加新的 RSS feed"""
    existing = db.query(RSSFeed).filter(RSSFeed.feed_url == feed.feed_url).first()
    if existing:
        raise HTTPException(status_code=400, detail="Feed already exists")
    
    new_feed = RSSFeed(**feed.dict())
    db.add(new_feed)
    db.commit()
    db.refresh(new_feed)
    
    # 立即获取一次 feed 内容
    await fetch_rss_feed(db, new_feed.id)
    
    return new_feed

@app.delete("/api/rss/feeds/{feed_id}")
async def delete_rss_feed(feed_id: int, db: Session = Depends(get_db)):
    """删除 RSS feed"""
    feed = db.query(RSSFeed).filter(RSSFeed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")
    
    db.query(RSSItem).filter(RSSItem.feed_id == feed_id).delete()
    db.delete(feed)
    db.commit()
    
    return {"message": "Feed deleted successfully"}

@app.get("/api/rss/items", response_model=List[RSSItemResponse])
async def get_rss_items(feed_id: Optional[int] = None, db: Session = Depends(get_db)):
    """获取 RSS items"""
    if feed_id:
        # 刷新特定 feed
        await fetch_rss_feed(db, feed_id)
        items = db.query(RSSItem).filter(RSSItem.feed_id == feed_id).order_by(RSSItem.published_at.desc()).all()
    else:
        # 获取所有 feeds
        items_data = await fetch_all_rss_items(db)
        # 转换回 ORM 对象用于响应
        items = db.query(RSSItem).order_by(RSSItem.published_at.desc()).limit(100).all()
    
    return items

@app.post("/api/rss/feeds/{feed_id}/refresh")
async def refresh_rss_feed(feed_id: int, db: Session = Depends(get_db)):
    """刷新特定 RSS feed"""
    feed = db.query(RSSFeed).filter(RSSFeed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")
    
    items = await fetch_rss_feed(db, feed_id)
    return {"message": f"Refreshed {len(items)} items", "feed": feed.title}

@app.get("/api/combined")
async def get_combined_items(limit: int = 50, db: Session = Depends(get_db)):
    """获取合并的 Hacker News 和 RSS items"""
    # 获取 HN stories
    hn_stories = await fetch_hn_top_stories(db, limit=limit//2)
    
    # 获取 RSS items
    rss_items_data = await fetch_all_rss_items(db)
    
    # 构建合并列表
    combined = []
    
    # 添加 HN stories
    for story in hn_stories:
        combined.append({
            "id": story.id,
            "type": "hn",
            "title": story.title,
            "url": story.url or f"https://news.ycombinator.com/item?id={story.hn_id}",
            "description": story.text,
            "author": story.by,
            "score": story.score,
            "time": story.time,
            "source": "Hacker News"
        })
    
    # 添加 RSS items
    for item_data in rss_items_data[:limit//2]:
        feed = db.query(RSSFeed).filter(RSSFeed.id == item_data['feed_id']).first()
        combined.append({
            "id": item_data['id'],
            "type": "rss",
            "title": item_data['title'],
            "url": item_data['link'],
            "description": item_data['description'],
            "author": None,
            "score": 0,
            "time": item_data['published_at'] or item_data['created_at'],
            "source": feed.title if feed else "RSS"
        })
    
    # 按时间排序
    combined.sort(key=lambda x: x['time'], reverse=True)
    
    return combined[:limit]

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
