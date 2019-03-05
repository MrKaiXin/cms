import base64
import pickle

from django_redis import get_redis_connection
from redis import StrictRedis
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from carts import serializers
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
                raise ValidationError('redis数据库操作失败, 购物车商品数量统计失败')
            # 统计总数量
            if values:
                for val in values:
                    count += int(val)
        else:  # 未登录
            carts = request.COOKIES.get('carts')

            # 统计总数量
            if carts:
                try:
                    carts = pickle.loads(base64.b64decode(carts.encode()))
                except Exception as e:
                    print('COOKIES错误', e)
                    raise ValidationError('COOKIES错误, 购物车修改商品失败')
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
            raise ValidationError('传入参数错误, 购物车添加商品失败')

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
                raise ValidationError('redis数据库操作失败, 购物车添加商品失败')

        else:  # 未登录
            carts = request.COOKIES.get('carts')

            # 保存商品数量到cookie中, 并将该商品选中
            if carts:
                try:
                    carts = pickle.loads(base64.b64decode(carts.encode()))
                except Exception as e:
                    print('COOKIES错误', e)
                    raise ValidationError('COOKIES错误, 购物车修改商品失败')
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
        """
        购物车商品查询
        """
        sku_list = []
        if request.user.is_authenticated():  # 登录
            user = request.user
            strict_redis = get_redis_connection('cart')  # type:StrictRedis

            try:
                cart = strict_redis.hgetall('cart_%s' % user.id)
                cart_selected = strict_redis.smembers('cart_selected_%s' % user.id)
            except Exception as e:
                print('redis数据库操作失败', e)
                raise ValidationError('redis数据库操作失败, 购物车商品查询失败')

            # 遍历每个商品,将商品所需的信息拼接后存到sku_list列表中
            for key, value in cart.items():
                try:
                    goods = Goods.objects.get(id=key)
                except Goods.DoesNotExist as e:
                    print('mysql数据库操作失败', e)
                    continue

                goods = serializers.GoodsSerializer(goods).data
                goods['sell_price'] = float(goods['sell_price'])
                goods['count'] = int(value)
                goods['selected'] = True if key in cart_selected else False
                sku_list.append(goods)
        else:  # 未登录
            carts = request.COOKIES.get('carts')

            if carts:
                try:
                    carts = pickle.loads(base64.b64decode(carts.encode()))
                except Exception as e:
                    print('COOKIES错误', e)
                    raise ValidationError('COOKIES错误, 购物车修改商品失败')

                # 遍历每个商品,将商品所需的信息拼接后存到sku_list列表中
                for key, value in carts.items():
                    try:
                        goods = Goods.objects.get(id=key)
                    except Goods.DoesNotExist as e:
                        print('mysql数据库操作失败', e)
                        continue
                    goods = serializers.GoodsSerializer(goods).data
                    goods['sell_price'] = float(goods['sell_price'])
                    goods['count'] = value['count']
                    goods['selected'] = value['selected']
                    sku_list.append(goods)

        return Response(sku_list)

    def put(self, request):
        """
        购物车商品数量修改及是否选中单个商品
        """
        data = request.data
        try:
            id = data.get('id')
            count = int(data.get('count'))
            selected = data.get('selected')
            Goods.objects.get(id=id)  # 如果查询不到该id的商品, 则报错
        except Exception as e:
            print('参数传入错误', e)
            raise ValidationError('传入参数错误, 购物车修改商品失败')

        response = Response({'message': 'OK'})
        if request.user.is_authenticated():  # 登录
            user = request.user
            strict_redis = get_redis_connection('cart')  # type:StrictRedis

            # 修改商品的数量和选中状态
            try:
                strict_redis.hset('cart_%s' % user.id, id, count)
                if selected:
                    strict_redis.sadd('cart_selected_%s' % user.id, id)
                else:
                    strict_redis.srem('cart_selected_%s' % user.id, id)
            except Exception as e:
                print('redis数据库操作失败', e)
                raise ValidationError('redis数据库操作失败, 购物车修改商品失败')
        else:  # 未登录
            carts = request.COOKIES.get('carts')

            # 修改商品的数量和选中状态
            if carts:
                try:
                    carts = pickle.loads(base64.b64decode(carts.encode()))
                except Exception as e:
                    print('COOKIES错误', e)
                    raise ValidationError('COOKIES错误, 购物车修改商品失败')
                carts[id]['count'] = count
                carts[id]['selected'] = selected
                print(carts)
                response.set_cookie('carts', base64.b64encode(pickle.dumps(carts)).decode(), constants.CART_COOKIE_EXPIRES)

        return response

    def delete(self, request):
        """
        购物车商品删除
        """
        data = request.data
        try:
            id = data.get('id')
            Goods.objects.get(id=id)  # 如果查询不到该id的商品, 则报错
        except Exception as e:
            print('参数传入错误', e)
            raise ValidationError('传入参数错误, 购物车修改商品失败')

        response = Response(status=204)
        if request.user.is_authenticated():  # 登录
            user = request.user
            strict_redis = get_redis_connection('cart')  # type:StrictRedis

            # 将商品从redis中删除
            try:
                strict_redis.hdel('cart_%s' % user.id, id)
                strict_redis.srem('cart_selected_%s' % user.id, id)
            except Exception as e:
                print('redis数据库操作失败', e)
                raise ValidationError('redis数据库操作失败, 购物车删除商品失败')
        else:  # 未登录
            carts = request.COOKIES.get('carts')

            # 将商品从COOKIES中删除
            if carts:
                try:
                    carts = pickle.loads(base64.b64decode(carts.encode()))
                except Exception as e:
                    print('COOKIES错误', e)
                    raise ValidationError('COOKIES错误, 购物车删除商品失败')
                del carts[id]
                print(carts)
                response.set_cookie('carts', base64.b64encode(pickle.dumps(carts)).decode(), constants.CART_COOKIE_EXPIRES)

        return response


class CartSelectAllView(APIView):
    def put(self, request):
        """
        购物车商品全选与全不选
        """
        selected = request.data.get('selected')
        if not isinstance(selected, bool):
            raise ValidationError('传入参数错误, 购物车全选或取消全选商品失败')

        response = Response({'message': 'OK'})
        if request.user.is_authenticated():  # 登录
            user = request.user
            strict_redis = get_redis_connection('cart')  # type:StrictRedis

            if selected:  # 全选
                try:
                    skus_id = strict_redis.hkeys('cart_%s' % user.id)
                    for id in skus_id:
                        strict_redis.sadd('cart_selected_%s' % user.id, id)
                except Exception as e:
                    print('redis数据库操作失败', e)
                    raise ValidationError('redis数据库操作失败, 购物车全选或取消全选商品失败')
            else:  # 取消全选
                try:
                    strict_redis.delete('cart_selected_%s' % user.id)
                except Exception as e:
                    print('redis数据库操作失败', e)
                    raise ValidationError('redis数据库操作失败, 购物车全选或取消全选商品失败')
        else:  # 未登录
            carts = request.COOKIES.get('carts')

            # 修改商品的数量和选中状态
            if carts:
                try:
                    carts = pickle.loads(base64.b64decode(carts.encode()))
                except Exception as e:
                    print('COOKIES错误', e)
                    raise ValidationError('COOKIES错误, 购物车全选或取消全选商品失败')

                for sku in carts.values():
                    sku['selected'] = selected
                response.set_cookie('carts', base64.b64encode(pickle.dumps(carts)).decode(),
                                    constants.CART_COOKIE_EXPIRES)

        return response


class CartClearView(APIView):
    def delete(self, request):
        """
        清空购物车
        """
        response = Response(status=204)
        if request.user.is_authenticated():  # 登录
            user = request.user
            strict_redis = get_redis_connection('cart')  # type:StrictRedis
            try:
                strict_redis.delete('cart_%s' % user.id)
                strict_redis.delete('cart_selected_%s' % user.id)
            except Exception as e:
                print('redis数据库操作失败', e)
                raise ValidationError('redis数据库操作失败, 购物车清空商品失败')

        else:  # 未登录
            carts = request.COOKIES.get('carts')

            # 清空购物车
            if carts:
                response.delete_cookie('carts')

        return response