from rest_framework import serializers

from news.models import News, NewsCategory


class NewSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['id', 'create_time', 'title', 'img_url', 'zhaiyao', 'content', 'author', 'click', 'is_slide']


class SonNewCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsCategory
        fields = ['id', 'title']


class NewCategorySerializer(serializers.ModelSerializer):
    newscategory_set = SonNewCategorySerializer(read_only=True, many=True)

    class Meta:
        model = NewsCategory
        fields = ['id', 'title', 'newscategory_set']
