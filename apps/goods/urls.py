from django.conf.urls import url

from goods import views

urlpatterns = [
    url(r'^goods/$', views.GoodsView.as_view()),
    url(r'^categories/(?P<pk>\d+)/$', views.GoodsListView.as_view()),
    url(r'^goods/(?P<pk>\d+)/$', views.GoodsDetailView.as_view()),
]
