from rest_framework import serializers
from goods.models import Goods, GoodsCategory, GoodsAlbum


class RecommendSerializer(serializers.ModelSerializer):

    class Meta:
        model = Goods
        fields = ['id', 'img_url', 'title', 'create_time']


class SubCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsCategory
        fields = ['id', 'title']


class CategorySerializer(serializers.ModelSerializer):
    goodscategory_set = SubCategorySerializer(read_only=True, many=True)

    class Meta:
        model = GoodsCategory
        fields = ['id', 'title', 'goodscategory_set']


class GoodsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Goods
        fields = ['id', 'title', 'img_url', 'sell_price', 'market_price', 'stock']


class ParentCategorySerializer(serializers.ModelSerializer):
    parent = SubCategorySerializer()

    class Meta:
        model = GoodsCategory
        fields = ['id', 'title', 'parent']


class GoodsAlbumSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsAlbum
        fields = ['thumb_path', 'original_path']


class GoodsDetailSerializer(serializers.ModelSerializer):
    category = ParentCategorySerializer()
    goodsalbum_set = GoodsAlbumSerializer(read_only=True, many=True)

    class Meta:
        model = Goods
        fields = ['id', 'category', 'goodsalbum_set', 'title', 'img_url', 'sub_title', 'goods_no', 'sell_price', 'market_price', 'stock']
