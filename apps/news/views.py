# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from news.models import News, NewsCategory
from news.serializer import NewSerializer, NewCategorySerializer


class NewTopAPIview(APIView):
    def get(self, request):
        try:
            # 查询轮播图新闻
            slide_query = News.objects.filter(is_slide=True).exclude(img_url="").all()
            # 查询推荐新闻
            news_recommendation = News.objects.order_by('-create_time')[0:10]
            # 查询img_url不为空，并且点击量 `click` 最多4条新闻
            picture_new = News.objects.exclude(img_url="").order_by('-click')[0:4]
        except News.DoesNotExist:
            return {'message': '查询的新闻不存在'}

        slide_news = NewSerializer(slide_query, many=True).data

        top_news = NewSerializer(news_recommendation, many=True).data

        image_news = NewSerializer(picture_new, many=True).data


        # 创建需要返回的
        data = {
            'slide_news': slide_news,

            'top_news': top_news,

            'image_news': image_news
        }
        return Response(data)


class CategoryNewAPIview(APIView):
    def get(self, request):
        # 获得所有的一级分类
        category_query = NewsCategory.objects.filter(parent_id=0).order_by('sort_id')
        # 创建序列化器对象,将数据序列化,得到字典数据
        category_list = []
        # print(category_query)
        # 遍历所有的一级类别
        for category in category_query:
            category_dict = NewCategorySerializer(category).data
            # 查出所有的一级类别下二级类别的ID
            s_categories = category.newscategory_set.all()
            # 遍历所有的二级类别,查出二级类别id的新闻
            s_list = []
            for s_category in s_categories:
                s_list.append(s_category.id)
            # 查询出所有所有category_id 在列表里的新闻
            category_news = News.objects.filter(category_id__in=s_list)

            # 将二级分类的新闻加入到字典中
            category_dict['news'] = NewSerializer(category_news.exclude(img_url="").order_by('-create_time')[0:4],
                                                  many=True).data
            # 将点击排行最多的八条数据加入到字典中
            category_dict['top8'] = NewSerializer(category_news.order_by('-click')[0:8], many=True).data
            category_list.append(category_dict)
        return Response(category_list)
