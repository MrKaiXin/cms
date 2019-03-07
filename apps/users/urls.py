"""cms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from users import views
from users.views import AddressViewSet

urlpatterns = [
    url(r'^userlogin/$', views.UserLoginView.as_view()),
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
    url(r'^mobile/(?P<mobile>((13[0-9])|(14[5,7])|(15[0-3,5-9])|(17[0,3,5-8])|(18[0-9])|166|198|199|(147))\d{8})/count/$',
        views.MobileCountView.as_view()),
    url(r'^users/$', views.CreateUserView.as_view()),
    url(r'^authorizations/$', views.UserAuthorizeView.as_view()),
    url(r'^user/$', views.UserDetailView.as_view()),
]

# 地址视图集接口的url
route = DefaultRouter()
route.register(r'addresses', AddressViewSet, base_name='addresses')
urlpatterns += route.urls
