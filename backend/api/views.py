from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from common.logger import logger 

from .models import RSSFeed, RSSItem, Story
from .serializers import RSSFeedSerializer, RSSItemSerializer, StorySerializer
from .services import fetch_all_rss_items, fetch_hn_top_stories, fetch_rss_feed, import_opml_feeds


class HNStoriesView(APIView):
    def get(self, request):
        limit = int(request.query_params.get("limit", 30))
        stories = fetch_hn_top_stories(limit=limit)
        serializer = StorySerializer(stories, many=True)
        return Response(serializer.data)


class RSSFeedsView(APIView):
    def get(self, request):
        feeds = RSSFeed.objects.all()
        serializer = RSSFeedSerializer(feeds, many=True)
        return Response(serializer.data)

    def post(self, request):
        feed_url = request.data.get("feed_url")
        if RSSFeed.objects.filter(feed_url=feed_url).exists():
            return Response(
                {"detail": "Feed already exists"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = RSSFeedSerializer(data=request.data)
        if serializer.is_valid():
            feed = serializer.save()
            fetch_rss_feed(feed.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RSSFeedDetailView(APIView):
    def delete(self, request, feed):
        feed = get_object_or_404(RSSFeed, id=feed)
        RSSItem.objects.filter(feed=feed).delete()
        feed.delete()
        return Response({"message": "Feed deleted successfully"})


class RSSFeedRefreshView(APIView):
    def post(self, request, feed):
        feed = get_object_or_404(RSSFeed, id=feed)
        items = fetch_rss_feed(feed.id)
        return Response(
            {"message": f"Refreshed {len(items)} items", "feed": feed.title}
        )


class RSSItemsView(APIView):
    def get(self, request):
        feed = request.query_params.get("feed")

        if feed:
            feed = get_object_or_404(RSSFeed, id=feed)
            fetch_rss_feed(feed.id)
            items = RSSItem.objects.filter(feed=feed).order_by("-published_at")
        else:
            fetch_all_rss_items()
            items = RSSItem.objects.order_by("-published_at")[:100]

        serializer = RSSItemSerializer(items, many=True)
        return Response(serializer.data)


class CombinedItemsView(APIView):
    def get(self, request):
        limit = int(request.query_params.get("limit", 50))

        logger.info("fetch hn top stories") 
        hn_stories = fetch_hn_top_stories(limit=limit // 2)
        logger.info(f"hn stories is {hn_stories}") 
        rss_items_data = fetch_all_rss_items()

        combined = []

        for story in hn_stories:
            combined.append(
                {
                    "id": story.id,
                    "type": "hn",
                    "title": story.title,
                    "url": story.url
                    or f"https://news.ycombinator.com/item?id={story.hn_id}",
                    "description": story.text,
                    "author": story.by,
                    "score": story.score,
                    "time": story.time.isoformat() if story.time else None,
                    "source": "Hacker News",
                }
            )

        for item_data in rss_items_data[: limit // 2]:
            feed = RSSFeed.objects.filter(id=item_data["feed"]).first()
            combined.append(
                {
                    "id": item_data["id"],
                    "type": "rss",
                    "title": item_data["title"],
                    "url": item_data["link"],
                    "description": item_data["description"],
                    "author": None,
                    "score": 0,
                    "time": item_data["published_at"] or item_data["created_at"],
                    "source": feed.title if feed else "RSS",
                }
            )

        combined.sort(key=lambda x: x["time"], reverse=True)
        return Response(combined[:limit])


@api_view(["GET"])
def root(request):
    return Response(
        {
            "message": "Hacker News + RSS Reader API",
            "docs": "/docs",
            "endpoints": {
                "hn_stories": "/api/hn/stories",
                "rss_feeds": "/api/rss/feeds",
                "rss_items": "/api/rss/items",
                "combined": "/api/combined",
            },
        }
    )


@api_view(["GET"])
def health_check(request):
    return Response({"status": "healthy"})


class OPMLImportView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response(
                {"error": "No file provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            file_content = file.read().decode('utf-8')
            result = import_opml_feeds(file_content)
            return Response({
                "message": f"Imported {len(result['added'])} feeds",
                "added": len(result['added']),
                "skipped": len(result['skipped']),
                "failed": len(result['failed']),
                "details": result
            })
        except Exception as e:
            return Response(
                {"error": f"Import failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
