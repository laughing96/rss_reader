from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/hackernews")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Story(Base):
    __tablename__ = "stories"
    
    id = Column(Integer, primary_key=True)
    hn_id = Column(Integer, unique=True, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=True)
    text = Column(Text, nullable=True)
    by = Column(String(100), nullable=False)
    score = Column(Integer, default=0)
    time = Column(DateTime, nullable=False)
    descendants = Column(Integer, default=0)
    type = Column(String(20), default="story")
    created_at = Column(DateTime, default=datetime.utcnow)

class RSSFeed(Base):
    __tablename__ = "rss_feeds"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False)
    feed_url = Column(String(1000), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_fetched = Column(DateTime, nullable=True)

class RSSItem(Base):
    __tablename__ = "rss_items"
    
    id = Column(Integer, primary_key=True)
    feed_id = Column(Integer, nullable=False)
    title = Column(String(500), nullable=False)
    link = Column(String(1000), nullable=False)
    description = Column(Text, nullable=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (Index('idx_feed_link', 'feed_id', 'link', unique=True),)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
