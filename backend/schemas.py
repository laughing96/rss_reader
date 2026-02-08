from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class StoryResponse(BaseModel):
    id: int
    hn_id: Optional[int]
    title: str
    url: Optional[str]
    text: Optional[str]
    by: str
    score: int
    time: datetime
    descendants: int
    type: str
    
    class Config:
        from_attributes = True

class RSSFeedCreate(BaseModel):
    title: str
    url: str
    feed_url: str
    description: Optional[str] = None

class RSSFeedResponse(BaseModel):
    id: int
    title: str
    url: str
    feed_url: str
    description: Optional[str]
    created_at: datetime
    last_fetched: Optional[datetime]
    
    class Config:
        from_attributes = True

class RSSItemResponse(BaseModel):
    id: int
    feed_id: int
    title: str
    link: str
    description: Optional[str]
    published_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class CombinedItem(BaseModel):
    id: int
    type: str  # 'hn' or 'rss'
    title: str
    url: str
    description: Optional[str]
    author: Optional[str]
    score: int
    time: datetime
    source: str
