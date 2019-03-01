from rest_framework import serializers

from goods.models import Goods


class GoodsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Goods
        fields = ['id', 'title', 'img_url', 'sell_price']
