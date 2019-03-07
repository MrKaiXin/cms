import random

from django_redis import get_redis_connection
from redis import StrictRedis
from rest_framework.response import Response
from rest_framework.views import APIView

from celery_tasks.sms.tasks import send_sms_code
from users.models import User

from utils import constants


class SMSCodeView(APIView):
    def get(self, request, mobile):
        strict_redis = get_redis_connection('verify_codes')  # type:StrictRedis
        send_flag = strict_redis.get('send_flag_%s' % mobile)

        if send_flag:
            return Response({'message': '发送短信过于频繁'}, status=400)

        try:
            User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            pass
        else:
            return Response({'message': '手机号已被注册'}, status=400)

        sms_code = random.randint(0, 999999)
        sms_code = '%06d' % sms_code

        send_sms_code.delay(mobile, sms_code)

        pipeline = strict_redis.pipeline()
        pipeline.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pipeline.setex('send_flag_%s' % mobile, constants.SEND_FLAG_REDIS_EXPIRES, 1)
        pipeline.execute()

        return Response({'message': 'OK'})
