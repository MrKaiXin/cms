from django.conf.urls import url

from carts import views

urlpatterns = [
    url(r'^carts/count/$', views.CartsCountView.as_view()),
    url(r'^cart/$', views.CartView.as_view()),
]

