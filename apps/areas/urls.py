from django.conf.urls import url

from areas import views

urlpatterns = [
    # 查询所有省份接口的url
    url(r'^areas/$', views.AreaProvinceView.as_view()),
    # 查询城市或区县数据接口的url
    url(r'^areas/(?P<pk>\d+)/$', views.SubAreaView.as_view())
]
