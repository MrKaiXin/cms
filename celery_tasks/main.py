from celery import Celery

import os
# 1. 设置配置文件, 需要放置到创建celery对象之前
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cms.settings")

# 2. 参数1: 自定义的一个名字
celery_app = Celery('cms', broker='redis://127.0.0.1:6379/15')

# 3. 指定要扫描任务的包, 会自动读取包下的名字为 tasks.py 的文件
celery_app.autodiscover_tasks(['celery_tasks.sms'])
