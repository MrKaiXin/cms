from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework_extensions.cache.mixins import ListCacheResponseMixin, RetrieveCacheResponseMixin

from areas.serializers import AreaSerializer, SubAreaSerializer
from users.models import Area


class AreaProvinceView(ListCacheResponseMixin, ListAPIView):
    """
    查询所有省份
    """
    queryset = Area.objects.filter(parent=None)
    serializer_class = AreaSerializer
    # 禁用分页功能
    pagination_class = None


class SubAreaView(RetrieveCacheResponseMixin, RetrieveAPIView):
    """
    查询一条城市或区县数据
    """
    queryset = Area.objects.all()
    serializer_class = SubAreaSerializer

