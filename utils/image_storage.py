from django.core.files.storage import FileSystemStorage

import logging

from libs.qiniu_storage import storage

logger = logging.getLogger('django')


class AvatarStorage(FileSystemStorage):
    def _save(self, name, content):
        with open(content, 'rb') as f:
            img_data = f.read()

        img_url = ''
        try:
            img_url = storage(img_data)
            print(img_url)
        except Exception as e:
            logger.error('骑牛云文件存储出错:', e)

        return img_url