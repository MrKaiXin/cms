from django_redis import get_redis_connection
from redis import StrictRedis
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import Goods


class CartsCountView(APIView):

    def get(self, request):
        """
        购物车商品数量统计
        """
        count = 0
        # 是否为登录状态
        if request.user.is_authenticated():  # 登录
            user = request.user
            strict_redis = get_redis_connection('cart')  # type:StrictRedis

            values = strict_redis.hvals('cart_%s' % user.id)
            print(values)
            # 统计总数量
            if values:
                for val in values:
                    count += int(val)
        else:  # 未登录
            carts = request.COOKIES.get('carts')
            print(carts)

            # 统计总数量
            if carts:
                for sku in carts:
                    count += sku['count']

        return Response({'count': count})


class CartView(APIView):

    def post(self, request):
        """
        购物车商品增加
        """
        data = request.data
        try:
            id = data.get('id')
            count = int(data.get('count'))
            Goods.objects.get(id=id)  # 如果查询不到该id的商品, 则报错
        except Exception as e:
            print(e)
            raise ValidationError('传入参数错误, 添加商品失败')

        # 是否为登录状态
        if request.user.is_authenticated():  # 登录
            user = request.user
            strict_redis = get_redis_connection('cart')  # type:StrictRedis

            try:
                value = int(strict_redis.hget('cart_%s' % user.id, id))  # 获取该id的商品在redis中的数量
            except Exception as e:
                value = 0

            # 保存商品数量到redis中, 并将该商品选中
            strict_redis.hset('cart_%s' % user.id, id, count+value)
            strict_redis.sadd('cart_selected_%s' % user.id, id)
        else:  # 未登录
            carts = request.COOKIES.get('carts')

            # 判断商品在不在cookie中,在则修改数量,不在则添加
            if carts:
                if id in carts:
                    carts[id]['count'] += count
                else:
                    carts[id] = {}
                    carts[id]['count'] = count
                carts[id]['selected'] = True

        # 返回添加状态
        return Response({'message': 'OK'})

