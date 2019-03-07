from django.contrib.auth.backends import ModelBackend
from django.db.models.query_utils import Q

from users.models import User


class UsernameMobileEmailAuthBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        query_set = User.objects.filter(Q(username=username) | Q(mobile=username) | Q(email=username))
        try:
            if query_set.exists():
                user = query_set.get()

                if user.check_password(password):
                    return user
        except Exception as e:
            print(e)
            return None


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'id': user.id,
        'username': user.username,
        'token': token
    }