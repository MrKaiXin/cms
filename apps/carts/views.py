import base64
import pickle

from django_redis import get_redis_connection
from redis import StrictRedis
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import Goods
from utils import constants


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

            try:
                values = strict_redis.hvals('cart_%s' % user.id)
            except Exception as e:
                print('redis数据库操作失败', e)
                raise ValidationError('redis数据库操作失败, 商品数量统计失败')
            # 统计总数量
            if values:
                for val in values:
                    count += int(val)
        else:  # 未登录
            carts = request.COOKIES.get('carts')

            # 统计总数量
            if carts:
                carts = pickle.loads(base64.b64decode(carts.encode()))
                print(carts)
                for sku in carts.values():
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
            print('参数传入错误', e)
            raise ValidationError('传入参数错误, 添加商品失败')

        response = Response({'message': 'OK'}, status=201)
        # 是否为登录状态
        if request.user.is_authenticated():  # 登录
            user = request.user
            strict_redis = get_redis_connection('cart')  # type:StrictRedis

            try:
                value = int(strict_redis.hget('cart_%s' % user.id, id))  # 获取该id的商品在redis中的数量
            except Exception as e:
                value = 0

            # 保存商品数量到redis中, 并将该商品选中
            try:
                strict_redis.hset('cart_%s' % user.id, id, count+value)
                strict_redis.sadd('cart_selected_%s' % user.id, id)
            except Exception as e:
                print('redis数据库操作失败', e)
                raise ValidationError('redis数据库操作失败, 添加商品失败')

        else:  # 未登录
            carts = request.COOKIES.get('carts')

            # 保存商品数量到cookie中, 并将该商品选中
            if carts:
                carts = pickle.loads(base64.b64decode(carts.encode()))
            else:
                carts = {}

            if id in carts:
                carts[id]['count'] += count
            else:
                carts[id] = {}
                carts[id]['count'] = count
            carts[id]['selected'] = True

            response.set_cookie('carts', base64.b64encode(pickle.dumps(carts)).decode(), constants.CART_COOKIE_EXPIRES)

        return response

    def get(self, request):

        if request.user.is_authenticated():  # 登录
            user = request.user
            strict_redis = get_redis_connection('cart')  # type:StrictRedis

            try:
                cart = strict_redis.hgetall('cart_%s' % user.id)
                cart_selected = strict_redis.smembers('cart_selected_%s' % user.id)
            except Exception as e:
                print('redis数据库操作失败', e)
                raise ValidationError('redis数据库操作失败, 商品数量统计失败')
            print(cart)  # {'2': '2', '1': '4', '89': '2'}
            print(cart_selected)  # {'2', '1', '89'}

        else:
            carts = request.COOKIES.get('carts')  # {97: {'count': 10, 'selected': True}, 90: {'count': 1, 'selected': True}, 94: {'count': 2, 'selected': True}, 95: {'count': 1, 'selected': True}}

            # 保存商品数量到cookie中, 并将该商品选中
            if carts:
                carts = pickle.loads(base64.b64decode(carts.encode()))
            else:
                carts = {}

            print(carts)
        return Response({'message': 'OK'})
