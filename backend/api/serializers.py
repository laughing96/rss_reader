from rest_framework import serializers
from .models import Story, RSSFeed, RSSItem, Folder


class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = '__all__'


class FolderSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    feed_count = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        fields = ['id', 'name', 'created_at', 'parent', 'children', 'feed_count']

    def get_children(self, obj):
        children = obj.children.all()
        return FolderSerializer(children, many=True).data

    def get_feed_count(self, obj):
        return obj.feeds.count()


class RSSFeedSerializer(serializers.ModelSerializer):
    folder_name = serializers.SerializerMethodField()
    folder_id = serializers.SerializerMethodField()

    class Meta:
        model = RSSFeed
        fields = ['id', 'title', 'url', 'feed_url', 'description',
                  'created_at', 'last_fetched', 'folder', 'folder_name', 'folder_id']

    def get_folder_name(self, obj):
        return obj.folder.name if obj.folder else None

    def get_folder_id(self, obj):
        return obj.folder.id if obj.folder else None


class RSSItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RSSItem
        fields = '__all__'


class CombinedItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField()
    title = serializers.CharField()
    url = serializers.CharField()
    description = serializers.CharField(allow_null=True)
    author = serializers.CharField(allow_null=True)
    score = serializers.IntegerField()
    time = serializers.DateTimeField()
    source = serializers.CharField()
