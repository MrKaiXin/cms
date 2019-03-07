from celery_tasks.main import celery_app
from libs.yuntongxun.sms import CCP
from utils import constants


@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    print(sms_code)
    # CCP().send_template_sms(mobile, [sms_code, int(constants.SMS_CODE_REDIS_EXPIRES/60)], 1)
