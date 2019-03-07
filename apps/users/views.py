import base64
import pickle

from django_redis import get_redis_connection
from redis import StrictRedis
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_jwt.views import ObtainJSONWebToken

from users.models import User
from users.serializers import CreateUserSerializer, UserDetailSerializer, UserAddressSerializer
from utils import constants


class UserLoginView(APIView):
    """
    判断用户是否登录或token是否过期
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'message': "OK"})


class UsernameCountView(APIView):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        data = {
            'username': username,
            'count': count
        }
        return Response(data)


class MobileCountView(APIView):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        data = {
            'mobile': mobile,
            'count': count
        }
        return Response(data)


class CreateUserView(CreateAPIView):
    serializer_class = CreateUserSerializer
    queryset = User.objects.all()
    throttle_classes = (AnonRateThrottle,)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        print(response)
        if response.status_code == 201:
            # 清空购物车
            carts = {}
            response.set_cookie('carts', base64.b64encode(pickle.dumps(carts)).decode(),
                                constants.CART_COOKIE_EXPIRES)
        return response


class UserDetailView(RetrieveAPIView, UpdateAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserAuthorizeView(ObtainJSONWebToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user_id = response.data['id']
            carts = request.COOKIES.get('carts')

            # 保存商品数量到cookie中, 并将该商品选中
            if carts:
                try:
                    carts = pickle.loads(base64.b64decode(carts.encode()))
                except Exception as e:
                    print('COOKIES错误', e)
                    carts = {}
            strict_redis = get_redis_connection('cart')  # type:StrictRedis
            for key, value in carts.items():
                # 保存商品数量到redis中, 并将该商品选中
                try:
                    strict_redis.hset('cart_%s' % user_id, key, value['count'])
                    if value['selected']:
                        strict_redis.sadd('cart_selected_%s' % user_id, key)
                except Exception as e:
                    print('redis数据库操作失败', e)

            carts = {}
            response.set_cookie('carts', base64.b64encode(pickle.dumps(carts)).decode(),
                                constants.CART_COOKIE_EXPIRES)
        return response


class AddressViewSet(CreateModelMixin, UpdateModelMixin, GenericViewSet):
    """ 用户地址管理
    1. 地址增删改查（查多条）
    2. 设置默认地址: put
    3. 设置地址标题: put
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'list' or self.action == 'update':
            return UserAddressSerializer

    def get_queryset(self):
        # 获取当前登录用户的所有地址
        return self.request.user.addresses.filter(is_deleted=False)

    def create(self, request, *args, **kwargs):
        """增加地址"""
        count = request.user.addresses.count()
        if count >= constants.ADDRESS_MAX_COUNT:
            return Response({'message': '地址个数已达到上限'}, status=400)

        response = super().create(request, *args, **kwargs)
        if response.status_code == 201:
            data = {
                'address': response.data,
                'default_address_id': request.user.default_address_id
            }
            return Response(data, status=201)
        return response

    def list(self, request):
        """查询所有地址"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = {
            'limit': constants.ADDRESS_MAX_COUNT,
            'user_id': request.user.id,
            'default_address_id': request.user.default_address_id,
            'addresses': serializer.data
        }
        return Response(data)

    def destroy(self, request, pk):
        """删除地址"""
        address = self.get_object()
        address.is_deleted = True
        address.save()

        request.user.default_address_id = None
        request.user.save()
        return Response({'message': 'OK'}, status=204)

    @action(methods=['put'], detail=True)
    def status(self, request, pk):
        """设置默认地址"""
        address = self.get_object()
        request.user.default_address_id = address.id
        request.user.save()
        return Response({'message': 'OK'})

    @action(methods=['put'], detail=True)
    def title(self, request, pk):
        """保存地址标题"""
        title = request.data.get('title')
        if not title:
            return Response({'message': '标题为空'}, status=400)

        address = self.get_object()
        address.title = title
        address.save()
        return Response({'message': 'OK'})