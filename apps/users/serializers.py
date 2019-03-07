import base64
import pickle
import re
from django_redis import get_redis_connection
from redis import StrictRedis
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.models import User, Area, Address


class CreateUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(label='确认密码', min_length=8, max_length=20, write_only=True)
    sms_code = serializers.CharField(label='短信验证码', max_length=6, write_only=True)
    allow = serializers.BooleanField(label='同意协议', default=False, write_only=True)
    token = serializers.CharField(label='登录状态token', read_only=True)

    def validate_mobile(self, value):
        if not re.match(r'((13[0-9])|(14[5,7])|(15[0-3,5-9])|(17[0,3,5-8])|(18[0-9])|166|198|199|(147))\d{8}', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def validate_allow(self, value):
        if value:
            return value
        else:
            raise serializers.ValidationError('请同意用户协议')

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError('两次密码不一致')

        sms_code = attrs.get('sms_code')
        mobile = attrs.get('mobile')
        strict_redis = get_redis_connection('verify_codes')  # type:StrictRedis
        real_sms_code = strict_redis.get('sms_%s' % mobile)

        if not real_sms_code:
            raise serializers.ValidationError('无效的短信验证码')

        if real_sms_code.decode() != sms_code:
            raise serializers.ValidationError('短信验证码错误')

        return attrs

    def create(self, validated_data):
        mobile = validated_data.get('mobile')
        if User.objects.filter(mobile=mobile).count() > 0:
            raise serializers.ValidationError('手机已被注册')

        user = User.objects.create_user(
            username=validated_data.get('username'),
            password=validated_data.get('password'),
            mobile=validated_data.get('mobile')
        )
        from rest_framework_jwt.settings import api_settings

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 生payload部分的方法(函数)
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 生成jwt的方法(函数)

        # user：登录的用户对象
        payload = jwt_payload_handler(user)  # 生成payload, 得到字典
        token = jwt_encode_handler(payload)  # 生成jwt字符串
        user.token = token

        carts = self.context['request'].COOKIES.get('carts')
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
                strict_redis.hset('cart_%s' % user.id, key, value['count'])
                if value['selected']:
                    strict_redis.sadd('cart_selected_%s' % user.id, key)
            except Exception as e:
                print('redis数据库操作失败', e)

        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'password2', 'mobile', 'sms_code', 'allow', 'token')
        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }


class UserDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'nick_name', 'gender', 'birthday', 'email', 'mobile', 'phone')


class UserAddressSerializer(serializers.ModelSerializer):
    """
    用户地址序列化器: 序列化 + 校验参数
    """
    # 序列化时返回省市区的名称
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)

    # 新增地址时需要传递省市区id
    province_id = serializers.IntegerField(label='省ID')
    city_id = serializers.IntegerField(label='市ID')
    district_id = serializers.IntegerField(label='区ID')

    def validate_mobile(self, value):
        """验证手机号"""
        if not re.match(r'^((13[0-9])|(14[57])|(15[0-35-9])|(17[035-8])|(18[0-9])|166|198|199|(147))\d{8}$', value):
            raise ValidationError('手机号格式错误')
        return value

    def validate(self, attrs):
        try:
            Area.objects.get(id=attrs.get('province_id'))
            Area.objects.get(id=attrs.get('city_id'))
            Area.objects.get(id=attrs.get('district_id'))
        except Address.DoesNotExist:
            raise ValidationError('无效省市区id')
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        address = super().create(validated_data)
        user.default_address_id = address.id
        user.save()
        return address

    class Meta:
        model = Address
        # 新增地址，不需要用户传递user到服务器，服务器可以自动获取到当前登录用户对象
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')