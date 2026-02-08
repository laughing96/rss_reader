from django.urls import path
from . import views

urlpatterns = [
    path(
        '',
        views.root,
        name='root'),
    path(
        'health/',
        views.health_check,
        name='health'),
    path(
        'api/hn/stories',
        views.HNStoriesView.as_view(),
        name='hn-stories'),
    path(
        'api/rss/feeds',
        views.RSSFeedsView.as_view(),
        name='rss-feeds'),
    path(
        'api/rss/feeds/<int:feed>',
        views.RSSFeedDetailView.as_view(),
        name='rss-feed-detail'),
    path(
        'api/rss/feeds/<int:feed>/refresh',
        views.RSSFeedRefreshView.as_view(),
        name='rss-feed-refresh'),
    path(
        'api/rss/items',
        views.RSSItemsView.as_view(),
        name='rss-items'),
    path(
        'api/combined',
        views.CombinedItemsView.as_view(),
        name='combined'),
    path(
        'api/rss/feeds/import',
        views.OPMLImportView.as_view(),
        name='rss-feeds-import'),
]
