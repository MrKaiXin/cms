from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import Goods, GoodsCategory
from goods.serializers import RecommendSerializer, GoodsSerializer, CategorySerializer, ParentCategorySerializer, \
    GoodsDetailSerializer


class GoodsView(APIView):

    def get(self, request):
        goods_dict = {}
        recommend_queryset = Goods.objects.filter(is_red=1).order_by("-sales")
        s = RecommendSerializer(recommend_queryset, many=True)
        goods_dict['recommend'] = s.data

        category1_queryset = GoodsCategory.objects.filter(parent=0)
        advertisement_list = []
        for category1 in category1_queryset:
            category1_serializer = CategorySerializer(category1)

            category2_queryset = GoodsCategory.objects.filter(parent_id=category1.id)
            category2_id_list = []

            for sub_category in category2_queryset:
                category2_id_list.append(sub_category.id)

            content_queryset = Goods.objects.filter(category_id__in=category2_id_list).order_by("-create_time")
            # print(len(content_queryset))
            content_serializer = GoodsSerializer(content_queryset, many=True)
            category_data = category1_serializer.data
            category_data["goods"] = content_serializer.data

            advertisement_list.append(category_data)

        goods_dict['advertisement'] = advertisement_list

        return Response(goods_dict)


class GoodsListView(APIView):

    # # 新增排序的过滤器
    # filter_backends = [OrderingFilter]
    # # 指定可以根据哪此字段进行排序
    # ordering_fields = ('create_time', 'sales', 'sell_price')

    def get(self, request, pk):
        ordering = request.query_params.get("ordering")
        ordering_list = ordering.split(',')
        # print(ordering_list)
        # print(type(ordering_list))

        category_obj = GoodsCategory.objects.get(id=pk)
        goods_dict = {}
        if not category_obj.parent_id:
            goods_dict["category_guide"] = ParentCategorySerializer(category_obj).data

            category2_id_list = []
            # sub_category_queryset = category_obj.category_set.all()
            sub_category_queryset = GoodsCategory.objects.filter(parent_id=category_obj.id)
            for sub_category in sub_category_queryset:
                category2_id_list.append(sub_category.id)
            content_queryset = Goods.objects.filter(category_id__in=category2_id_list).order_by(*ordering_list)

            goods_dict["goods_content"] = GoodsSerializer(content_queryset, many=True).data
        else:
            goods_dict["category_guide"] = ParentCategorySerializer(category_obj).data

            sub_content_queryset = Goods.objects.filter(category_id=category_obj.id).order_by(*ordering_list)
            goods_dict["goods_content"] = GoodsSerializer(sub_content_queryset, many=True).data

        return Response(goods_dict)


class GoodsDetailView(APIView):

    def get(self, request, pk):
        goods_dict = {}
        recommend_queryset = Goods.objects.filter(is_red=1).order_by("-sales")
        s = RecommendSerializer(recommend_queryset, many=True)
        goods_dict['recommend'] = s.data

        goods_obj = Goods.objects.get(id=pk)
        goods_dict['goods_detail'] = GoodsDetailSerializer(goods_obj).data

        return Response(goods_dict)
