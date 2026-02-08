from rest_framework import serializers
from .models import Story, RSSFeed, RSSItem


class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = '__all__'


class RSSFeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = RSSFeed
        fields = '__all__'


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
